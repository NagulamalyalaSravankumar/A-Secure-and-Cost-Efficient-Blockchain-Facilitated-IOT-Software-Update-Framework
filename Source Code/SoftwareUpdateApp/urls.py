from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('ManufactureLogin.html', views.ManufactureLogin, name="ManufactureLogin"), 
	       path('OwnerLogin.html', views.OwnerLogin, name="OwnerLogin"), 
	       path('Register.html', views.Register, name="Register"),
	       path('Signup', views.Signup, name="Signup"),
	       path('UserLogin', views.UserLogin, name="UserLogin"),
	       path('Upload.html', views.Upload, name="Upload"),
	       path('ViewPayments', views.ViewPayments, name="ViewPayments"),
	       path('UploadAction.html', views.UploadAction, name="UploadAction"),
	       path('ViewBlocks', views.ViewBlocks, name="ViewBlocks"),
	       path('PurchaseUpdates', views.PurchaseUpdates, name="PurchaseUpdates"),
	       path('MakePayment', views.MakePayment, name="MakePayment"),
	       path('MakePaymentAction', views.MakePaymentAction, name="MakePaymentAction"),
	       path('ViewOwnerPayments', views.ViewOwnerPayments, name="ViewOwnerPayments"),
]