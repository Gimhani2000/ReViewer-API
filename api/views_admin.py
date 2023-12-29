from rest_framework.views import APIView
from django.db.models import Q
from . models import User , Book
from . serializers_admin import  BookSerializer
from . serializers import AccountSerializer
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import  permission_classes , parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser , FormParser

# get users view : this view return users with paginations and reaech terms
# only accessible for admin
# serializer : AccountSerializer in serializers.py
@permission_classes([IsAuthenticated])
class getUsers(APIView):
    def post(self,request):
        if request.user.is_superuser:
            active = request.data["status"]
            page = request.data["page"]
            search = None;
            if "search" not in request.data or request.data["search"] == "":
                users = User.objects.filter(is_superuser=0 , is_active=(active == "active")).order_by("name")
            else:
                search = request.data["search"]
                users = User.objects.filter((Q(name__icontains=search) | Q(email__icontains=search)) & Q(is_superuser=0)).order_by("name")

            paginator = Paginator(users, 25)
            paginated_users = paginator.get_page(page)
            serializer = AccountSerializer(paginated_users , many = True)
            return Response({"users":serializer.data , 
                            "meta":{
                                "count":paginator.count , 
                                "page_count":paginator.num_pages,
                                "start":paginated_users.start_index(),
                                "end":paginated_users.end_index()
                                }
                            })
        else:
            raise PermissionDenied({"details":"You don't have permission to this action."})

# chnage user status : admin can user account activate or deactivate through this
# only accessible for admin
@permission_classes([IsAuthenticated])
class changeUserStatus(APIView):
    def post(self,request):
        if request.user.is_superuser:
            active = request.data["status"]
            users = User.objects.get(email = request.data["email"])
            users.is_active = (active == "active")
            users.save()
            return Response({
                "details":"success"
            })
        else:
            raise PermissionDenied({"details":"You don't have permission to this action."})

# add new book view : admin can add new book with this view.
# only accessible for admin
# it will return success , error or raise PermissionDenied exception
# serializer : BookSerializer in serializers_admin.py
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser , FormParser])
class addNewBook(APIView):
    def post(self,request):
        if request.user.is_superuser:
            try:
                isbn = request.data["isbn"]
                book = Book.objects.filter(isbn=isbn).first()

                # check isbn already exist or not
                if book is not None:
                    return Response({
                    "isbn" : "This isbn already registered"
                })
                serializer = BookSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({
                    "details" : "success"
                })
            except KeyError:
                return Response({
                    "details":"error"
                })
        else:
            raise PermissionDenied({"details":"You don't have permission to this action."})