from .views import LeaveApplication, LeaveApprovalView,LeaveHistory,  LeaveRequestList, ApproveLeaveRequest, RejectLeaveRequest
from django.urls import path

urlpatterns = [
    path('apply-leave/',LeaveApplication.as_view(),name='apply-leave'),
    path('approve-leave/<int:pk>/', LeaveApprovalView.as_view(), name='approve-leave'),
    path('leave-history/', LeaveHistory.as_view(), name='leave-history'),


    path('leave/requests/', LeaveRequestList.as_view(), name='leave-request-list'),
    path('leave/approve/', ApproveLeaveRequest.as_view(), name='approve-leave-request'),
    path('leave/reject/', RejectLeaveRequest.as_view(), name='reject-leave-request'),
]