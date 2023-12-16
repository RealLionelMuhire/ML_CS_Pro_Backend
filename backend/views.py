# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
# from django.contrib.auth import authenticate, login, logout, get_user_model
# from django.urls import reverse
# from django.db import IntegrityError
# from rest_framework import status, filters
# from django.http import JsonResponse, Http404, HttpResponseBadRequest
# from rest_framework.authtoken.models import Token
# from rest_framework.decorators import api_view, permission_classes
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from .serializers import UserSerializer, ActionSerializer, ClientSerializer
# from rest_framework.authtoken.views import obtain_auth_token
# from datetime import timedelta
# from django.utils import timezone
# from .models import Client, Action, CustomUser, PasswordResetToken, UserActionLog
# from rest_framework import generics
# from decimal import Decimal
# from django.shortcuts import get_object_or_404
# from rest_framework.views import APIView
# from django.db.models import Sum, F
# from rest_framework.generics import CreateAPIView
# from django.core.mail import send_mail
# from django.utils.crypto import get_random_string
# from django.contrib.auth.hashers import make_password
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from django.core.mail import send_mail
# from django.views import View
# from django.urls import reverse
# from django.middleware.csrf import get_token
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.models import Permission
# from django.contrib.auth.decorators import permission_required
# from django.utils.decorators import method_decorator


# # class HelloWorldView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         content = {'message': 'Hello, World!'}
# #         return Response(content)

# # class RegistrationView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request):
# #         if not request.user.has_perm('auth.can_create_user'):
# #             return Response({'message': 'Permission denied. You do not have the required permission to create a user.'}, status=status.HTTP_403_FORBIDDEN)

# #         # Include the registered_by_id and registered_by_fullname in the request data
# #         request.data['registered_by_id'] = request.user.UserID
# #         print(f"the user who is registering has an id {request.user.UserID}")
# #         request.data['registered_by_fullname'] = request.user.FullName
# #         print(f"the user who is registering has name {request.user.FullName}")


# #         serializer = UserSerializer(data=request.data)
# #         try:
# #             if serializer.is_valid():
# #                 user = serializer.save()
# #                 return JsonResponse({'message': 'Registration successful', 'user_id': user.UserID})
# #             else:
# #                 return Response({'message': 'Registration failed', 'errors': serializer.errors}, status=400)
# #         except IntegrityError as e:
# #             print(f"IntegrityError: {e}")
# #             return Response({'message': 'Registration failed. Duplicate user.'}, status=status.HTTP_400_BAD_REQUEST)

# # class UserPermissionsView(APIView):

# #     def get(self, request):
# #         user_permissions = request.user.user_permissions.all()
# #         permission_names = [permission.name for permission in user_permissions]
# #         return Response({'user_permissions': permission_names})

# # class AllPermissionsView(APIView):
# #     def get(self, request):
# #         all_permissions = Permission.objects.all()
# #         permission_names = [permission.name for permission in all_permissions]
# #         return Response({'all_permissions': permission_names})

# # class ActivateUserView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     @method_decorator(permission_required('auth.can_activate_user', raise_exception=True))
# #     def post(self, request, user_id):
# #         try:
# #             user = CustomUser.objects.get(pk=user_id)
            
# #             if not user.is_active:
# #                 # If the user is not activated, activate and send welcome email
# #                 user.is_active = True
# #                 user.save()

# #                 # Log the activation and send a response
# #                 UserActionLog.objects.create(user=user, action_type='Activate User', permission=user.user_permissions.last(), granted_by=request.user, granted_by_fullname=request.user.FullName)
# #                 return Response({'message': 'User activated successfully. Welcome email sent.'})
# #             else:
# #                 # If the user is already activated, skip activation and return a response
# #                 return Response({'message': 'User is already activated.'})
# #         except CustomUser.DoesNotExist:
# #             return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# # class DeactivateUserView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     @method_decorator(permission_required('auth.can_deactivate_user', raise_exception=True))
# #     def post(self, request, user_id):
# #         try:
# #             user = CustomUser.objects.get(pk=user_id)
# #             if user.is_active:
# #                 # If the user is activated, deactivate
# #                 user.is_active = False
# #                 user.save()

# #                 # Log the deactivation and send a response
# #                 UserActionLog.objects.create(user=user, action_type='Deactivate User', permission=user.user_permissions.last(), granted_by=request.user, granted_by_fullname=request.user.FullName)
# #                 return Response({'message': 'User Deactivated successfully'})
# #             else:
# #                 # If the user is already deactivated, skip deactivation and return a response
# #                 return Response({'message': 'User is already deactivated.'})
# #         except CustomUser.DoesNotExist:
# #             return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# # class GrantPermissionsView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     @method_decorator(permission_required('auth.can_grant_permissions', raise_exception=True))
# #     def post(self, request, user_id):
# #         try:
# #             # Check if the requesting user has the permission 'can_grant_permissions'
# #             if not request.user.has_perm('auth.can_grant_permissions'):
# #                 return Response({'message': 'Permission denied. You do not have the required permission to grant permissions.'}, status=status.HTTP_403_FORBIDDEN)

# #             user_to_grant = CustomUser.objects.get(pk=user_id)

# #             # Check if the requesting user has the permission to grant the specified permissions
# #             if not request.user.has_perm('auth.can_grant_permissions'):
# #                 return Response({'message': 'Permission denied. You do not have the required permission to grant the specified permissions.'}, status=status.HTTP_403_FORBIDDEN)

# #             # Your logic to grant permissions goes here
# #             user_to_grant.user_permissions.add(Permission.objects.get(codename='can_create_user'))
# #             user_to_grant.user_permissions.add(Permission.objects.get(codename='can_activate_user'))
# #             user_to_grant.user_permissions.add(Permission.objects.get(codename='can_deactivate_user'))

# #             UserActionLog.objects.create(user=user_to_grant, action_type='Grant Permissions', granted_by=request.user)
            
# #             return Response({'message': 'Permissions granted successfully'})
# #         except CustomUser.DoesNotExist:
# #             return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

# # @api_view(['POST'])
# # @permission_classes([AllowAny])
# # def login_view(request):
# #     # Extract username (email) and password from the request data
# #     print("testing login")
# #     email = request.data.get('email').strip()
# #     password = request.data.get('password').strip()

# #     # Perform authentication using the email
# #     user = authenticate(request, email=email, password=password)
# #     if user is not None:
# #         # Log in the user
# #         login(request, user)

# #         # Generate a new token with a 45-minute expiration time
# #         token, created = Token.objects.get_or_create(user=user)
# #         expiration_time = timezone.now() + timedelta(minutes=1)  # Adjust as needed
# #         token.created = timezone.now()
# #         token.save()

# #         # Serialize the user data
# #         serializer = UserSerializer(user)
# #         user_data = serializer.data

# #         return Response({'message': 'Login successful', 'user_id': user_data['UserID'], 'token': token.key})
# #     else:
# #         return Response({'message': 'Login failed'}, status=400)


# # @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# # def logout_view(request):
# #     # Log out the user and invalidate the token
# #     user = request.user
# #     logout(request)
# #     request.auth.delete()

# #     # Close all active actions initiated by the user
# #     active_actions = Action.objects.filter(user=user, is_active=True)
# #     for action in active_actions:
# #         action.end_time = timezone.now()
# #         action.is_active = False
# #         action.save()
# #         print("Closing actions done")

# #     return Response({'message': 'Logout successful'})

# # class ClientRegistrationView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request):
# #         # Retrieve the user from the authenticated request
# #         user = request.user

# #         # Combine the user data with the client data
# #         request_data = request.data
# #         request_data['user'] = user.UserID  # Replace 'id' with the actual field in your CustomUser model

# #         # Create the serializer
# #         serializer = ClientSerializer(data=request_data)

# #         try:
# #             if serializer.is_valid():
# #                 # Save the client with the associated user
# #                 client = serializer.save()
# #                 return Response({'message': 'Client registration successful', 'client_id': client.id})
# #             else:
# #                 return Response({'message': 'Client registration failed', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
# #         except IntegrityError as e:
# #             print(f"IntegrityError: {e}")
# #             return Response({'message': 'Client registration failed. Duplicate client.'}, status=status.HTTP_400_BAD_REQUEST)

# # class ClientDeleteView(generics.DestroyAPIView):
# #     queryset = Client.objects.all()
# #     serializer_class = ClientSerializer
# #     permission_classes = [IsAuthenticated]

# #     def destroy(self, request, *args, **kwargs):
# #         try:
# #             client = self.get_object()
# #             # Check if the authenticated user is the owner of the client
# #             if request.user != client.user:
# #                 return Response({'message': 'You do not have permission to delete this client.'}, status=status.HTTP_403_FORBIDDEN)
            
# #             client.delete()
# #             return Response({'message': 'Client deleted successfully'})
# #         except Client.DoesNotExist:
# #             return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)

# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def search_clients(request):
# #     # Get query parameters from the request
# #     search_query = request.query_params.get('q', '')

# #     # Perform the search
# #     clients = Client.objects.filter(full_name__icontains=search_query)

# #     # Serialize the results
# #     serializer = ClientSerializer(clients, many=True)

# #     return Response(serializer.data)

# # class ListClientsView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         clients = Client.objects.all()

# #         # Serialize the results
# #         serializer = ClientSerializer(clients, many=True)

# #         return Response(serializer.data)

# # class AddFieldToClientView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request, client_id):
# #         # Get the client instance
# #         try:
# #             client = Client.objects.get(id=client_id)
# #         except Client.DoesNotExist:
# #             return Response({'message': 'Client not found'}, status=404)

# #         # Check if the user has permission to modify this client
# #         if request.user != client.user:
# #             return Response({'message': 'Permission denied'}, status=403)

# #         # Get the field value from the request data
# #         field_value = request.data.get('new_field', None)

# #         # Add the new field to the client
# #         if field_value is not None:
# #             client.new_field = field_value
# #             client.save()
# #             return Response({'message': 'Field added successfully'})
# #         else:
# #             return Response({'message': 'Invalid field value'}, status=400)

# # class InitiateActionView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request, client_id):
# #         user = request.user
# #         try:
# #             client = Client.objects.get(id=client_id)
# #         except Client.DoesNotExist:
# #             raise Http404("Client does not exist 404 or not registered")

# #         title = request.data.get('title')

# #         # Check for an existing unclosed action with the same title
# #         existing_action = Action.objects.filter(
# #             client=client,
# #             title=title,
# #             end_time__isnull=True  # Unclosed actions
# #         ).first()

# #         if existing_action:
# #             return Response({'message': 'An unclosed action with the same title already exists.'}, status=status.HTTP_400_BAD_REQUEST)

# #         data = {
# #             'user': user.UserID,
# #             'client': client.id,
# #             'title': request.data.get('title'),
# #             'objective': request.data.get('objective'),
# #         }

# #         serializer = ActionSerializer(data=data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response({'message': 'Action initiated successfully'})
# #         else:
# #             return Response({'message': 'Failed to initiate action', 'errors': serializer.errors}, status=400)

# # class CloseActionView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request, action_id):
# #         try:
# #             action = Action.objects.get(id=action_id, is_active=True)
# #         except Action.DoesNotExist:
# #             return Response("Action does not exist or is not active.")

# #         if action.start_time is None:
# #             return Response({'message': 'Cannot close uninitiated action.'}, status=status.HTTP_400_BAD_REQUEST)
        
# #         if action.is_active == False:
# #             return Response({'message': 'action already closed'}, status=status.HTTP_400_BAD_REQUEST)

# #          # Check if the user initiating the action is the same as the user who initiated it   
# #         if request.user == action.user:
# #             action.end_time = timezone.now()
# #             action.description = request.data.get('description', None)

# #             elapsed_time_seconds = (action.end_time - action.start_time).total_seconds()
# #             elapsed_time_minutes = Decimal(elapsed_time_seconds) / Decimal(60)  # Convert seconds to minutes

# #             action.total_elapsed_time += elapsed_time_minutes
# #             action.is_active = False
# #             action.save()

# #             serializer = ActionSerializer(action)
# #             return Response({'message': 'Action closed successfully', 'action': serializer.data})
# #         else:
# #             return Response({'message': 'You do not have permission to close this action'}, status=403)

# # class ActionListView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         user = request.user
# #         client_id = self.request.query_params.get('client')
# #         title = self.request.query_params.get('title')
# #         is_active = self.request.query_params.get('is_active')
# #         user_id = self.request.query_params.get('user')

# #         queryset = Action.objects.filter(user=user)

# #         # Filter by client ID
# #         if client_id:
# #             queryset = queryset.filter(client_id=client_id)

# #         # Filter by title
# #         if title:
# #             queryset = queryset.filter(title=title)

# #         # Filter by is_active
# #         if is_active:
# #             queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
# #         # filter by user
# #         if user_id:
# #             queryset = Action.objects.filter(user_id=user_id)

# #         # Calculate total elapsed time
# #         queryset = queryset.annotate(sum_elapsed_time=Sum('total_elapsed_time'))

# #         # Sort by default from newest to oldest
# #         queryset = queryset.order_by('-start_time')

# #         # Serialize the queryset
# #         serializer = ActionSerializer(queryset, many=True)
# #         serialized_data = serializer.data

# #         return Response(serialized_data, status=status.HTTP_200_OK)

# def send_password_reset_email(user_email, reset_link):
#     subject = 'Password Reset'
#     message = f'Click the following link to reset your password: {reset_link}'
#     from_email = 'muhirelionel@gmail.com'  # replace with your email
#     recipient_list = [user_email]

#     send_mail(subject, message, from_email, recipient_list, fail_silently=False)

# class ForgotPasswordView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         print('==> Start Trying Forgot PWD ==>')
#         # Get user email from request.data
#         email = request.data.get('email')

#         try:
#             # Find the user with the provided email
#             user = CustomUser.objects.get(email=email)
#         except CustomUser.DoesNotExist:
#             return Response({'message': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

#         # Generate token for the user
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)

#         print('==> User Found ==>')

#         # Construct the reset link
#         reset_link = reverse('reset-password', kwargs={'uidb64': uid, 'token': token})

#         # For localhost testing, prepend the link with http://localhost:8000
#         reset_link = 'http://localhost:8000' + reset_link

#         # Save the token to the database
#         token_obj = PasswordResetToken.objects.create(user=user, token=token, expiration_time=timezone.now() + timedelta(days=1))

#         # Send the email with the reset link
#         send_password_reset_email(email, reset_link)

#         return Response({'message': 'Password reset email sent'})


# # User = get_user_model()
# # class ResetPasswordView(APIView):
# #     permission_classes = [AllowAny]

# #     def get(self, request, uidb64, token):
# #         try:
# #             uid = force_str(urlsafe_base64_decode(uidb64))
# #             user = User.objects.get(pk=uid)
# #         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
# #             user = None

# #         # Check if the user and token are valid
# #         if user is not None and default_token_generator.check_token(user, token):
# #             # Render a password reset form
# #             print(f"Rendering password reset form for user: {user}")
# #             return render(request, 'password_reset_form.html', {'uidb64': uidb64, 'token': token})
# #         else:
# #             # Token is not valid
# #             print(f"Invalid token or user not found. User: {user}, Token: {token}")
# #             return HttpResponseBadRequest('Invalid token or user not found.')

# #     permission_classes = [AllowAny]

# #     def post(self, request, uidb64, token):
# #         print(f"Received POST request for password reset with token: {token}")

# #         # Additional print statements for debugging
# #         print(f"Received uidb64: {uidb64}")
        
# #         # Your existing code to handle password reset
# #         try:
# #             uid = force_str(urlsafe_base64_decode(uidb64))
# #             user = User.objects.get(pk=uid)
# #             print(f"User found: {user.email}")
# #         except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
# #             print(f"Error finding user: {e}")
# #             return HttpResponseBadRequest('Invalid token or user not found.')

# #         # Print values for debugging
# #         print(f"Token: {token}")
# #         print(f"User: {user}")

# #         # Check if the token exists in the database
# #         if PasswordResetToken.objects.filter(token=token, user=user, expiration_time__gt=timezone.now()).exists():
# #             print(f"Token data found for user: {user.email}")

# #             # Retrieve the token data
# #             token_data = PasswordResetToken.objects.get(token=token, user=user, expiration_time__gt=timezone.now())
            
# #             new_password = request.data.get('new_password')
# #             user.password = make_password(new_password)
# #             user.save()

# #             print(f"Password reset successful for user: {user.email}")

# #             # Delete the used token
# #             token_data.delete()

# #             return Response({'message': 'Password reset successful'})
# #         else:
# #             print(f"Token data not found for user: {user.email}")
# #             return HttpResponseBadRequest('Invalid token or user not found.')

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_dashboard_data(request):
#     # Your logic to fetch dashboard data
#     data = {'user': request.user.FullName, 'message': 'Welcome to the dashboard!'}
#     return Response(data)
