
import json
from django.http import  HttpResponse
from django.shortcuts import render
import csv
from datetime import datetime, timedelta
import asyncio
from datetime import datetime


def upload_csv(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        timeframe = int(request.POST['timeframe'])
        print('got the file')

        candles = []
        # Process uploaded CSV file
        reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
        print('readding the file')
        
        for row in reader:
            candles.append(row)
        print('data has been saved in model')
        
        # Convert candles to timeframe
        converted_candles = asyncio.run(convert_to_timeframe(candles, timeframe=timeframe))
  

        # Save JSON to file
        json_file_path = 'file.json'  # Replace with actual path where you want to save the JSON file
        with open(json_file_path, 'w') as f:
            f.write(converted_candles)

        # Return JSON file as response
        with open(json_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="output.json"'
            return response
    return render(request, 'upload.html')  # Replace 'upload.html' with your template name


async def convert_to_timeframe(candles, timeframe):

    converted_candles = []
    current_timeframe_start = None
    aggregated_candle = None
    timeframe_delta = timedelta(minutes=timeframe)
    # print(candles);   

    for candle in candles:

        candle_date = datetime.strptime(f"{candle['DATE']} {candle['TIME']}", "%Y%m%d %H:%M")
        
        # Initialize timeframe start time
        if current_timeframe_start is None:
            current_timeframe_start = candle_date
        
        # Check if current candle is within the current timeframe
        if candle_date < current_timeframe_start + timeframe_delta:
            if aggregated_candle is None:
                aggregated_candle = {
                    'BANKNIFTY': candle['BANKNIFTY'],
                    'DATE': candle['DATE'],
                    'TIME': candle['TIME'],
                    'OPEN': float(candle['OPEN']),
                    'HIGH': float(candle['HIGH']),
                    'LOW': float(candle['LOW']),
                    'CLOSE': float(candle['CLOSE']),
                    'VOLUME': int(candle['VOLUME']),
                }
            else:
                aggregated_candle['HIGH'] = max(aggregated_candle['HIGH'], float(candle['HIGH']))
                aggregated_candle['LOW'] = min(aggregated_candle['LOW'], float(candle['LOW']))
                aggregated_candle['CLOSE'] = float(candle['CLOSE'])
                aggregated_candle['VOLUME'] = candle['VOLUME']
                

        else:
            # End of current timeframe, store aggregated candle and reset
            if aggregated_candle:
                converted_candles.append(aggregated_candle)
            aggregated_candle = None
            current_timeframe_start = candle_date
    
    # Append the last aggregated candle if exists
    if aggregated_candle:
        converted_candles.append(aggregated_candle)
    
    # Convert candles to JSON
    candles_json = json.dumps(converted_candles, default=str)  # Convert Python objects to JSON string

    return candles_json
