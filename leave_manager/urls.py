from .views import LeaveApplication, LeaveApprovalView,LeaveHistory,  LeaveRequestList, ApproveLeaveRequest, RejectLeaveRequest, DashbaordLeaveHistory,EmployeeListView, AllLeaveRequestsView, CreateEmployeeView, DashboardRequestsView, DashboardStatsView
from django.urls import path

urlpatterns = [
    path('apply-leave/',LeaveApplication.as_view(),name='apply-leave'),
    path('approve-leave/<int:pk>/', LeaveApprovalView.as_view(), name='approve-leave'),
    path('leave-history/', LeaveHistory.as_view(), name='leave-history'),
    path('dashboard/datas/', DashbaordLeaveHistory.as_view(), name='leave-history'),


    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('leave/requests/', LeaveRequestList.as_view(), name='leave-request-list'),
    path('leave/approve/', ApproveLeaveRequest.as_view(), name='approve-leave-request'),
    path('leave/reject/', RejectLeaveRequest.as_view(), name='reject-leave-request'),
    path('leave/all-requests/', AllLeaveRequestsView.as_view(), name='all-leave-requests'),
    path('employees/create/', CreateEmployeeView.as_view(), name='create-employee'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/requests/', DashboardRequestsView.as_view(), name='dashboard-requests'),

]