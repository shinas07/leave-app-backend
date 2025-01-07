from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
# Create your views here.

# Employee Logic
class LeaveApplication(APIView):
    permission_class = [IsAuthenticated]
    def post(self, request):
        print(request.data)
        print(request.user)
        serializer = LeaveRequestSerializer(data=request.data)
        if serializer.is_valid():
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']
            if start_date.weekday() == 6 or end_date.weekday() == 6:
                return Response({'error':"Leave cannot be applied for Sunday."}, status=status.HTTP_400_BAD_REQUEST)
            leave_request = serializer.save(user=request.user)
            return Response(LeaveRequestSerializer(leave_request).data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class LeaveHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leave_requests = LeaveRequest.objects.filter(user=request.user)
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        print(serializer.date)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
# Manager Logic
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


class LeaveRequestList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leave_requests = LeaveRequest.objects.all()  # Fetch all leave requests
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
