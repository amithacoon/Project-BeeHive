import io
import os
import sys
import os
import shutil
from django.shortcuts import render, HttpResponse
from .forms import UploadCSVForm

import pandas as pd
import csv
from django.shortcuts import render, HttpResponse
from openpyxl.reader.excel import load_workbook
import google.generativeai as genai
from .forms import UploadCSVForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time
prompt1 = "קח את הטקסט הבא בעברית וסכם את הבעיה החברתית איתה מתמודד הפרויקט עד 75 מילים."
prompt2 = "קח את הטקסט הבא בעברית וסכם את האתגר הספציפי שהמיזם מנסה לפתור בשני משפטים."
prompt3 = "קח את הטקסט הבא בעברית ותאר כיצד המיזם נותן מענה לאתגר הספציפי בשני משפטים."
prompt4 = "קח את הסיכומים הבאים וכתוב סיכום חדש על המיזם באורך של עד 90 מילים. תן דגש לקראת הסוף לדרך הפעולה במיזם"
prompt5 = "קח את הטקסט הבא בעברית וסכם מה נעשה עד היום במיזם למשפט אחד עד 30 מילים."
prompt6 = "קח את הסיכומים הבאים וכתוב סיכום חדש על המיזם באורך למשפט אחד בעברית"
prompt7 = " קח את הטקסט הבא בעברית וסכם בשורה אחת בלבד את המודל העסקי של הפרויקט, החזר רק את הסיכום בשורה עד 20 מילים"


def gemini(prompt, text):
    model_name = 'gemini-1.5-flash'  # Replace with an available model name if needed
    model = genai.GenerativeModel(model_name)
    genai.configure(api_key='AIzaSyB3h0w_rzHYiaFDP6PJ5VqiBw3l8sKF3hA')
    combined =prompt + text
    response = model.generate_content(combined)
    text = response.candidates[0].content.parts[0].text
    return (text)


prompt1 = "קח את הטקסט הבא בעברית וסכם את הרקע של היזם/יזמים למשפט אחד."


def clear_media_directory():
    media_dir = 'media/'
    if os.path.exists(media_dir):
        shutil.rmtree(media_dir)  # Remove the directory and all its contents
    os.makedirs(media_dir)  # Create a new empty directory

def handle_uploaded_file(f):
    with open(f'media/{f.name}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def csv_upload_view(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            clear_media_directory()  # Clear the media directory before uploading the new file
            file = request.FILES['csv_file']
            handle_uploaded_file(file)
            return display_csv(request, file)
    else:
        form = UploadCSVForm()
    return render(request, 'home.html', {'form': form})

def handle_uploaded_file(f):
    with open(f'media/{f.name}', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)



def display_csv(request, f):
    file_path = f'media/{f.name}'
    extension = os.path.splitext(file_path)[1].lower()

    if extension == '.csv':
        data = read_csv_file(file_path)
    elif extension in ['.xls', '.xlsx']:
        data = read_excel_file(file_path)
    else:
        return HttpResponse("Unsupported file type")

    if not data:
        return HttpResponse("No data found in file")

    headers = data[0]
    rows = data[1:]

    return render(request, 'display.html', {'headers': headers, 'rows': rows})

def display_csv_2(request, filename):
    file_path = os.path.join('media/download', filename)
    extension = os.path.splitext(file_path)[1].lower()

    if extension == '.csv':
        data = read_csv_file(file_path)
    elif extension in ['.xls', '.xlsx']:
        data = read_excel_file(file_path)
    else:
        return HttpResponse("Unsupported file type")

    if not data:
        return HttpResponse("No data found in file")

    headers = data[0]
    rows = data[1:]

    return render(request, 'display.html', {'headers': headers, 'rows': rows})

def read_csv_file(file_path):
    data = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)
    except Exception as e:
        return HttpResponse(f"Error reading CSV file: {e}")
    return data


def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path)
        data = df.values.tolist()
        headers = df.columns.tolist()
        data.insert(0, headers)  # Ensure headers are the first row
    except Exception as e:
        return HttpResponse(f"Error reading Excel file: {e}")
    return data

# Set standard output to use UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
def load_excel_to_dataframe(file_path):
    """
    Load an Excel file into a pandas DataFrame.

    Parameters:
    file_path (str): The path to the Excel file.

    Returns:
    pd.DataFrame: The loaded DataFrame.
    """
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print("Excel file loaded successfully!")
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None


from threading import Lock

# Global variables for progress
progress = 0
progress_lock = Lock()

def update_progress(value):
    global progress
    with progress_lock:
        progress = value

def get_progress():
    global progress
    with progress_lock:
        return progress


def process_dataframe(df, column_number, newname, prompt1, result_df=None):
    global progress
    results = []
    total_rows = len(df) - 1

    for i in range(1, len(df)):
        text = str(df.iloc[i, column_number])
        result = gemini(prompt1, text)
        results.append(result)

        # Update progress
        update_progress((i / total_rows) * 100)

    new_column_df = pd.DataFrame(results, columns=[newname])

    if result_df is None:
        result_df = pd.DataFrame(index=df.index)

    result_df = result_df.join(new_column_df)
    return result_df

from django.http import JsonResponse



from django.http import JsonResponse

from django.http import JsonResponse

def get_progress_view(request):
    return JsonResponse({'progress': get_progress()})



def asis_df(df, column_number, newname, result_df=None):
    # Initialize an empty list to store results
    results = []

    # Extract the text from the specified column
    for i in range(1, len(df)):
        text = str(df.iloc[i, column_number])
        results.append(text)

    # Create a new DataFrame from the results list
    new_column_df = pd.DataFrame(results, columns=[newname])

    # If result_df is not provided, create a new DataFrame with the same index as df
    if result_df is None:
        result_df = pd.DataFrame(index=df.index)

    # Add the new column to the result DataFrame
    result_df = result_df.join(new_column_df)

    return result_df


def save_dataframe(df, format, rtl=True):
    directory = 'media/download'
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = os.path.join(directory, 'Updated_Table')

    # Apply RTL override for CSV if required
    if rtl and format.lower() == 'csv':
        rlo = '\u202E'
        df = df.applymap(lambda x: rlo + str(x) if isinstance(x, str) else x)

    if format.lower() == 'csv':
        full_filename = filename + '.csv'
        df.to_csv(full_filename, index=False, encoding='utf-8-sig')
        print(f"DataFrame saved as {full_filename} with UTF-8 encoding and RTL orientation")
    elif format.lower() == 'xlsx':
        full_filename = filename + '.xlsx'
        df.to_excel(full_filename, index=False)
        if rtl:
            # Load the workbook and select the active sheet
            wb = load_workbook(full_filename)
            ws = wb.active

            # Set the sheet to RTL orientation
            ws.sheet_view.rightToLeft = True

            # Save the modified workbook with RTL support
            wb.save(full_filename)
            print(f"DataFrame saved as {full_filename} with RTL orientation")
        else:
            print(f"DataFrame saved as {full_filename}")
    else:
        raise ValueError("Unsupported format. Please choose either 'csv' or 'xlsx'.")




def get_tags_activity(df, result_df=None):
    global progress
    results = []
    model_name = 'gemini-1.5-flash'  # Replace with an available model name if needed
    model = genai.GenerativeModel(model_name)
    genai.configure(api_key='AIzaSyB3h0w_rzHYiaFDP6PJ5VqiBw3l8sKF3hA')
    tag_list = ["תעסוקה", "מוביליות חברתית", "חינוך והשכלה", "בריאות נפשית", "בריאות", "אחר", "קהילה"]

    for i in range(len(df)):
        text = str(df.iloc[i, 10])
        print(text)
        prompt = f"Given the next Hebrew text: '{text}', which of these tags is the best match?   {tag_list}. Return only the tag and nothing else, return one!. "

        response = model.generate_content(prompt)

        results.append(response.candidates[0].content.parts[0].text)

        # Update progress
    newname = "תג -  תחום חברתי"
    new_column_df = pd.DataFrame(results, columns=[newname])

    if result_df is None:
        result_df = pd.DataFrame(index=df.index)

    result_df = result_df.join(new_column_df)
    return result_df


def get_tags_age(df, result_df=None):
    global progress
    results = []
    model_name = 'gemini-1.5-flash'  # Replace with an available model name if needed
    model = genai.GenerativeModel(model_name)
    genai.configure(api_key='AIzaSyB3h0w_rzHYiaFDP6PJ5VqiBw3l8sKF3hA')
    tag_list = ["הגיל הרך", "ילדים ונוער", "צעירים", "הזדקנות מיטבית, אנשים מעל גיל 90", "אחר"]

    for i in range(len(df)):
        text = str(df.iloc[i, 10])
        print(text)
        prompt = f"Given the next Hebrew text: '{text}', which of these tags is the best match?   {tag_list}. Return only the tag and nothing else, return one!. "

        response = model.generate_content(prompt)
        results.append(response.candidates[0].content.parts[0].text)

        # Update progress
    newname = "תג- קבוצת גיל"
    new_column_df = pd.DataFrame(results, columns=[newname])

    if result_df is None:
        result_df = pd.DataFrame(index=df.index)

    result_df = result_df.join(new_column_df)
    return result_df


def get_tags_population(df, result_df=None):
    global progress
    results = []
    model_name = 'gemini-1.5-flash'  # Replace with an available model name if needed
    model = genai.GenerativeModel(model_name)
    genai.configure(api_key='AIzaSyB3h0w_rzHYiaFDP6PJ5VqiBw3l8sKF3hA')
    tag_list = ["החברה הערבית", "החברה החרדית", 'קהילת הלהט"ב', "קהילת יוצאי אתיופיה",
                           "אוכלוסיות בסיכון ומצבי קצה", "אנשים עם מוגבלות", "אחר"]
    for i in range(len(df)):
        text = str(df.iloc[i, 10])
        print(text)
        prompt = f"Given the next Hebrew text: '{text}', which of these tags is the best match?   {tag_list}. Return only the tag and nothing else, return one!. "

        response = model.generate_content(prompt)
        results.append(response.candidates[0].content.parts[0].text)

        # Update progress
    newname = "תג - אוכלסיית יעד"
    new_column_df = pd.DataFrame(results, columns=[newname])

    if result_df is None:
        result_df = pd.DataFrame(index=df.index)

    result_df = result_df.join(new_column_df)
    return result_df



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import time

@csrf_exempt
def run_df(request):
    if request.method == 'POST':
        file = request.FILES.get('csv_file')
        if not file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        format = request.POST.get('format', 'csv')
        file_path = f'media/{file.name}'
        handle_uploaded_file(file)

        # Load the file into a DataFrame
        df = load_excel_to_dataframe(file_path)

        if df is None:
            return JsonResponse({'error': 'Failed to load file into DataFrame'}, status=400)

        total_stages = 4  # Number of main stages in processing
        current_stage = 0

        # Process the DataFrame in stages and update progress
        df = process_dataframe(df, 11, 'תקציר על מודל הפעולה ', prompt1, df)
        current_stage += 1
        update_progress((current_stage / total_stages) * 100)

        df = process_dataframe(df, 14, 'תקציר בשורה ', prompt1, df)
        current_stage += 1
        update_progress((current_stage / total_stages) * 100)

        df = get_tags_activity(df, df)
        current_stage += 1
        update_progress((current_stage / total_stages) * 100)

        df = get_tags_age(df, df)
        current_stage += 1
        update_progress((current_stage / total_stages) * 100)

        df = get_tags_population(df, df)
        current_stage += 1
        update_progress((current_stage / total_stages) * 100)

        # Save the DataFrame
        save_dataframe(df, format=format)

        # Return the filename in the JSON response
        filename = f'Updated_Table.{format}'
        return JsonResponse({'result': '', 'filename': filename})
    return JsonResponse({'error': 'Invalid request'}, status=400)
