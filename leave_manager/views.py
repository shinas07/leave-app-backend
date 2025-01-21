from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LeaveRequest, YearlyLeaveBalance
from .serializers import LeaveRequestSerializer, EmployeeSerializer, CreateEmployeeSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from rest_framework import generics
from django.db.models import Count, Q, Sum
from .permissions import IsManager
from datetime import datetime

# Create your views here.

# Employee Logic

from datetime import timedelta


class LeaveApplication(APIView):
    permission_classes = [IsAuthenticated]

    def get_or_create_yearly_balance(self, user, year):
        balance, created = YearlyLeaveBalance.objects.get_or_create(
            user=user,
            year=year,
            defaults={'total_leaves': 40, 'leaves_taken': 0}
        )
        return balance

    def get_total_leaves_count(self, user, year):
        # Get approved leaves
        approved_leaves = LeaveRequest.objects.filter(
            user=user,
            status='approved',
            start_date__year=year
        ).aggregate(total=Sum('duration'))['total'] or 0

        # Get pending leaves
        pending_leaves = LeaveRequest.objects.filter(
            user=user,
            status='pending',
            start_date__year=year
        ).aggregate(total=Sum('duration'))['total'] or 0

        return approved_leaves, pending_leaves

    def post(self, request):
        serializer = LeaveRequestSerializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']

            # Basic validations
            if start_date > end_date:
                return Response(
                    {'error': 'Start date cannot be greater than the end date.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            if start_date == end_date and start_date.weekday() == 6:
                return Response(
                    {'error': "Leave cannot be applied for Sunday."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check for overlapping requests
            overlapping_requests = LeaveRequest.objects.filter(
                user=request.user,
                start_date__lte=end_date,
                end_date__gte=start_date
            )

            if overlapping_requests.exists():
                # Check specific status of overlapping requests
                approved_requests = overlapping_requests.filter(status='approved')
                pending_requests = overlapping_requests.filter(status='pending')
                
                if approved_requests.exists():
                    return Response(
                        {'error': 'Leave is already approved for these dates.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                elif pending_requests.exists():
                    return Response(
                        {'error': 'You already have a pending leave request for these dates.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    # If all overlapping requests are rejected
                    return Response(
                        {'error': 'You have previously applied for these dates and it was rejected. '
                                'Please consider discussing with your manager before reapplying.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Calculate duration without saving
            temp_leave_request = LeaveRequest(
                user=request.user,
                start_date=start_date,
                end_date=end_date
            )
            leave_duration = temp_leave_request.calculate_duration()

            # Get or create yearly balance
            year_balance = self.get_or_create_yearly_balance(request.user, start_date.year)

            # Get total approved and pending leaves
            approved_leaves, pending_leaves = self.get_total_leaves_count(request.user, start_date.year)

            # Calculate total leaves including the new request
            total_leaves = approved_leaves + pending_leaves + leave_duration

            if total_leaves > year_balance.total_leaves:
                return Response({
                    'error': f'Insufficient leave balance for year {start_date.year}. \n'
                            f'Total leaves: {year_balance.total_leaves} days\n'
                            f'Approved leaves: {approved_leaves} days\n'
                            f'Pending leaves: {pending_leaves} days\n'
                            f'Requested: {leave_duration} days\n'
                            f'Available: {year_balance.total_leaves - (approved_leaves + pending_leaves)} days'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Only save if all validations pass
            leave_request = serializer.save(
                user=request.user,
                status='pending',
                duration=leave_duration
            )

            return Response(
                LeaveRequestSerializer(leave_request).data, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardLeaveHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get_or_create_yearly_balance(self, user, year):
        balance, created = YearlyLeaveBalance.objects.get_or_create(
            user=user,
            year=year,
            defaults={'total_leaves': 40, 'leaves_taken': 0}
        )
        return balance

    def get(self, request):
        current_year = timezone.now().year
        
        # Get or create balance for current year
        year_balance = self.get_or_create_yearly_balance(request.user, current_year)

        # Fetch the last 5 leave requests
        leave_requests = LeaveRequest.objects.filter(
            user=request.user
        ).order_by('-id')[:5]
        
        serializer = LeaveRequestSerializer(leave_requests, many=True)

        # Calculate total approved leaves for current year
        approved_leaves_total = LeaveRequest.objects.filter(
            user=request.user,
            status='approved',
            start_date__year=current_year
        ).aggregate(total=Sum('duration'))['total'] or 0

        # Count statistics for current year
        pending_leaves = LeaveRequest.objects.filter(
            user=request.user, 
            status='pending',
            start_date__year=current_year
        ).count()

        approved_leaves_count = LeaveRequest.objects.filter(
            user=request.user, 
            status='approved',
            start_date__year=current_year
        ).count()

        rejected_leaves = LeaveRequest.objects.filter(
            user=request.user, 
            status='rejected',
            start_date__year=current_year
        ).count()

        # Update leaves_taken based on approved leaves only
        year_balance.leaves_taken = approved_leaves_total
        year_balance.save()

        response_data = {
            'leave_history': serializer.data,
            'stats': {
                'totalLeaves': year_balance.total_leaves,
                'usedLeaves': year_balance.leaves_taken,  # This will be approved leaves only
                'pendingLeaves': pending_leaves,
                'approvedLeaves': approved_leaves_count,
                'rejectedLeaves': rejected_leaves,
                'remainingLeaves': year_balance.remaining_leaves,  # This will update based on approved leaves only
                'year': current_year
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    


class LeaveHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leave_requests = LeaveRequest.objects.filter(user=request.user)
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
# Manager Logic
class EmployeeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = EmployeeSerializer
    queryset = User.objects.filter(user_type=User.UserType.EMPLOYEE)
    
class LeaveApprovalView(APIView):
    permission_class = [IsAuthenticated, IsManager]
    def patch(self, request, pk):
        try:
            leave_request = LeaveRequest.objects.get(pk=pk)
            if request.user.is_staff:
                leave_request.status = request.data.get('status', leave_request.status)
                leave_request.save()
                return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_200_OK)
            return Response({"error": "You do not have permission to approve this leave."}, status=status.HTTP_403_FORBIDDEN)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)


class AllLeaveRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsManager]
    serializer_class = LeaveRequestSerializer

    def get_queryset(self):
        return LeaveRequest.objects.all().order_by('-created_at')
     
class LeaveRequestList(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        leave_requests = LeaveRequest.objects.filter(status='pending')  # Fetch all leave requests
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ApproveLeaveRequest(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        request_id = request.data.get('requestId')
        try:
            leave_request = LeaveRequest.objects.get(id=request_id)
            leave_request.status = 'approved'
            leave_request.save()
            return Response({'message': 'Leave request approved successfully!'}, status=status.HTTP_200_OK)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

class RejectLeaveRequest(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        request_id = request.data.get('requestId')
        try:
            leave_request = LeaveRequest.objects.get(id=request_id)
            leave_request.status = 'rejected'
            leave_request.save()
            return Response({'message': 'Leave request rejected successfully!'}, status=status.HTTP_200_OK)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)


class CreateEmployeeView(generics.CreateAPIView):
    serializer_class = CreateEmployeeSerializer
    permission_classes = [IsAuthenticated,IsManager]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Employee created successfully',
                'user_type': serializer.validated_data['user_type']
            }, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        # Get counts for different types of requests
        leave_stats = LeaveRequest.objects.aggregate(
            pending_count=Count('id', filter=Q(status='pending')),
            approved_count=Count('id', filter=Q(status='approved')),
            rejected_count=Count('id', filter=Q(status='rejected'))
        )

        # Get total employees count (excluding admin)
        total_employees = User.objects.filter(user_type='employee').count()

        return Response({
            'totalEmployees': total_employees,
            'pendingRequests': leave_stats['pending_count'],
            'approvedRequests': leave_stats['approved_count'],
            'rejectedRequests': leave_stats['rejected_count']
        })

class DashboardRequestsView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        # Get recent leave requests (last 10)
        recent_requests = LeaveRequest.objects.select_related('user').order_by('-created_at')[:10]
        serializer = LeaveRequestSerializer(recent_requests, many=True)
        return Response(serializer.data)