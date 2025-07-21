from rest_framework import serializers

class DailyEnergySerializer(serializers.Serializer):
    Hour = serializers.IntegerField()
    Energy_Predicted = serializers.FloatField()
    Energy_LowerBound = serializers.FloatField()

    class Meta:
        fields = ['Hour', 'Energy_Predicted', 'Energy_LowerBound']