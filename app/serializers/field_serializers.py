from rest_framework import serializers


class ChangePasswordDetailSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, required=True)
    new_password = serializers.CharField(max_length=128, required=True)


class StudentLoginDetailSerializer(serializers.Serializer):
    registration_no = serializers.CharField(max_length=20, required=True)
    password = serializers.CharField(max_length=128, required=True)


class GroupRequestSerializer(serializers.Serializer):
    student_2_id = serializers.IntegerField(required=True)
    project_category = serializers.IntegerField(required=True)
