from rest_framework import serializers
from super_admin.models import Country, NoteCategory, NoteType
from authenticate.models import User
from notes.models import Downloads, SellerNotesReviews

class ContactUsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.CharField(required=True)
    comment = serializers.CharField(required=True)

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name", "code"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteCategory
        fields = ["id", "name", "description"]

class NoteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteType
        fields = ["id", "name", "description"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "profile_picture"]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password", "is_superuser", "is_staff", "user_permissions"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        return representation
    
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    date_of_birth = serializers.DateTimeField(allow_blank=True)
    gender = serializers.CharField(required=True)
    phone_country_code = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    profile_picture = serializers.CharField(required=True)
    address_line_one = serializers.CharField(required=True)
    address_line_two = serializers.CharField(allow_blank=True)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    zip_code = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    university = serializers.CharField(allow_blank=True)
    college = serializers.CharField(allow_blank=True)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'email': {'required': False}, 'password': {'required': False}}

    def validate(self, attrs):
        email = attrs.get("email")
        phone_country_code = attrs.get("phone_country_code")
        country = attrs.get('country')
        user = self.context.get("user")

        if not User.objects.filter(id=user.id, role_id=3).exists():
            raise serializers.ValidationError('User is not exist.')
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            raise serializers.ValidationError("Email already exists.")
        if not Country.objects.filter(id=int(phone_country_code)).exists():
            raise serializers.ValidationError('Country code is not exist.')
        if not Country.objects.filter(id=int(country)).exists():
            raise serializers.ValidationError('Country is not exist.')
        return attrs
    
class AdminProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    phone_country_code = serializers.CharField(allow_blank=True)
    phone_number = serializers.CharField()
    profile_picture = serializers.CharField()

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'email': {'required': False}, 'password': {'required': False}}

    def validate(self, attrs):
        email = attrs.get("email")
        phone_country_code = attrs.get("phone_country_code")
        user = self.context.get("user")

        if not User.objects.filter(id=user.id, role_id=2).exists():
            raise serializers.ValidationError('User is not exist.')
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            raise serializers.ValidationError("Email already exists.")
        if not Country.objects.filter(id=int(phone_country_code)).exists():
            raise serializers.ValidationError('Country code is not exist.')
        return attrs
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerNotesReviews
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['created_by'] = UserSerializer(instance.created_by).data
        # representation['note'] = NoteSerializer(instance.note).data
        representation['modified_by'] = UserSerializer(instance.modified_by).data
        representation['reviewed_by'] = UserSerializer(instance.reviewed_by).data
        # representation['against_downloads'] = DownloadSerializer(instance.against_downloads).data
        return representation
    
class AddReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(required=True)
    comment = serializers.CharField(required=True)
    download_id = serializers.IntegerField(required=True)

    def validate(self, attrs):
        download_id = attrs.get("download_id")
        user = self.context.get("user")

        if not Downloads.objects.filter(id=download_id, downloader=user, is_seller_has_allowed_to_download=True).exists():
            raise serializers.ValidationError("Note is not exist on your download.")
        if SellerNotesReviews.objects.filter(against_downloads__id=download_id).exists():
            raise serializers.ValidationError("Your review exist against this note.")
        return attrs