from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer, EmployeeSerializer, CreateEmployeeSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from rest_framework import generics
from django.db.models import Count, Q
# Create your views here.

# Employee Logic
class LeaveApplication(APIView):
    permission_class = [IsAuthenticated]
    def post(self, request):
        serializer = LeaveRequestSerializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']
            if start_date.weekday() == 6 or end_date.weekday() == 6:
                print('working here')
                return Response({'error':"Leave cannot be applied for Sunday."}, status=status.HTTP_400_BAD_REQUEST)

            overlapping_requests = LeaveRequest.objects.filter(
                user=request.user,
                start_date__lte=end_date,
                end_date__gte=start_date
            )

            if overlapping_requests.exists():
                return Response({'error':'you already have a leave request for the selected dates.'},status=status.HTTP_400_BAD_REQUEST)
            
            total_leaves_taken = LeaveRequest.objects.filter(user=request.user).count()
            
            if total_leaves_taken >= 40:
                return Response({'error': 'You have already exhausted your leave quota for the year.'}, status=status.HTTP_400_BAD_REQUEST)
            

            leave_request = serializer.save(user=request.user)
            return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class DashbaordLeaveHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch the last 5 leave requests for the authenticated user
        leave_requests = LeaveRequest.objects.filter(user=request.user).order_by('-id')[:5]
        serializer = LeaveRequestSerializer(leave_requests, many=True)

        # Calculate statistics
        total_leaves = LeaveRequest.objects.filter(user=request.user).count()  # Total leaves taken
        pending_leaves = LeaveRequest.objects.filter(user=request.user, status='pending').count()
        approved_leaves = LeaveRequest.objects.filter(user=request.user, status='approved').count()
        rejected_leaves = LeaveRequest.objects.filter(user=request.user, status='rejected').count()
        remaining_leaves = 40 - total_leaves  # Assuming 40 total leaves allocated

        # Prepare the response data
        response_data = {
            'leave_history': serializer.data,
            'stats': {
                'totalLeaves': total_leaves,
                'pendingLeaves': pending_leaves,
                'approvedLeaves': approved_leaves,
                'rejectedLeaves': rejected_leaves,
                'remainingLeaves': remaining_leaves,
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
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeSerializer
    queryset = User.objects.filter(user_type=User.UserType.EMPLOYEE)
class LeaveApprovalView(APIView):
    permission_class = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveRequestSerializer

    def get_queryset(self):
        return LeaveRequest.objects.all().order_by('-created_at')
     
class LeaveRequestList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leave_requests = LeaveRequest.objects.filter(status='pending')  # Fetch all leave requests
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ApproveLeaveRequest(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get recent leave requests (last 10)
        recent_requests = LeaveRequest.objects.select_related('user').order_by('-created_at')[:10]
        serializer = LeaveRequestSerializer(recent_requests, many=True)
        return Response(serializer.data)