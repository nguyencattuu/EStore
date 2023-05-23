from django.shortcuts import render
from django.conf import settings
from analysis.utils import *
import pandas as pd


# Create your views here.
def analysis(request):
    # Likes
    csv_data_likes = settings.MEDIA_ROOT + 'store/analysis/data_likes.csv'
    likes = pd.read_csv(csv_data_likes)
    df_likes_html = likes.to_html()

    # Views
    csv_data_views = settings.MEDIA_ROOT + 'store/analysis/data_views.csv'
    views = pd.read_csv(csv_data_views)
    df_views_html = views.to_html()

    csv_data = settings.MEDIA_ROOT + 'store/analysis/data.csv'
    data = pd.read_csv(csv_data)
    df_data_html = data.to_html()

    return render(request, 'analysis/series_dataframe.html', {
        'df_likes_html': df_likes_html,
        'df_views_html': df_views_html,
        'df_data_html': df_data_html,
    })


def chart(request):
    # Histogram
    data_wait_times = settings.MEDIA_ROOT + 'store/analysis/dataset.xlsx'
    data_second = pd.read_excel(data_wait_times, sheet_name='Wait_times')
    hist = get_hist(data_second, 'seconds', 'Customer Wait Time')

    return render(request, 'analysis/chart.html', {
        'hist': hist,
    })
