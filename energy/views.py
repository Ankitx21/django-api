import pandas as pd
import numpy as np
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, time
from .serializers import DailyEnergySerializer
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@api_view(['GET'])
def energy_predictions(request):
    # Use environment variable for CSV directory if set, else default to local path
    csv_dir = os.environ.get('CSV_DIR', "E:/ankit_iihs_projects/classification_30_days/v18_output/")
    today = datetime.now().date()  # Current date: 2025-07-18
    csv_file = f"next_24_hrs_v18_68_{today}.csv"

    csv_path = os.path.join(csv_dir, csv_file)
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        yesterday = (datetime.now() - pd.Timedelta(days=1)).date()
        csv_file = f"next_24_hrs_v18_68_{yesterday}.csv"
        csv_path = os.path.join(csv_dir, csv_file)
        try:
            df = pd.read_csv(csv_path)
        except FileNotFoundError:
            return JsonResponse({"error": "No CSV file found for today or yesterday"}, status=404)

    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df[(df['datetime'].dt.time >= time(6, 0)) & (df['datetime'].dt.time <= time(18, 0))]

    # Calculate time differences and cumulative time within the filtered dataframe
    time_diffs = (df['datetime'] - df['datetime'].shift()).dt.total_seconds().fillna(0) / 3600
    cum_time = time_diffs.cumsum()

    df['hour'] = df['datetime'].dt.hour
    hourly_data = df.groupby('hour').agg({
        'mean_predicted_irradiance': 'mean',  # Use mean for now, adjust integration below
        'Lower_Bound': 'mean'  # Use mean for now, adjust integration below
    }).reset_index()

    # Perform integration over the original data for each hour
    response_data = {}
    for hour in hourly_data['hour'].unique():
        hour_df = df[df['hour'] == hour]
        if not hour_df.empty:
            time_diffs_hour = (hour_df['datetime'] - hour_df['datetime'].shift()).dt.total_seconds().fillna(0) / 3600
            cum_time_hour = time_diffs_hour.cumsum()
            energy_predicted = np.trapezoid(hour_df['mean_predicted_irradiance'], x=cum_time_hour)
            lower_bound = np.trapezoid(hour_df['Lower_Bound'], x=cum_time_hour)
            
            hourly_data_dict = {
                "Hour": int(hour),
                "Energy_Predicted": round(energy_predicted, 2),
                "Energy_LowerBound": round(lower_bound, 2)
            }
            serializer = DailyEnergySerializer(data=hourly_data_dict)
            if serializer.is_valid():
                if today.strftime('%Y-%m-%d') not in response_data:
                    response_data[today.strftime('%Y-%m-%d')] = []
                response_data[today.strftime('%Y-%m-%d')].append(serializer.data)

    return Response(response_data)

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        csv_file = request.FILES['file']
        save_path = os.path.join(os.environ.get('CSV_DIR', '/tmp/'), csv_file.name)
        with open(save_path, 'wb+') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)
        return JsonResponse({'status': 'success', 'filename': csv_file.name})
    return JsonResponse({'error': 'No file uploaded'}, status=400)