from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from .forms import AudioForm

from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource 
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions, ConceptsOptions, EmotionOptions, KeywordsOptions, RelationsOptions, SentimentOptions

from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator



def authentication():
    apikey_t = "65AmPrVbHCgZNblbl_f-Ue3NtSierVXYOayv4hY9TjCq"
    url_t = "https://api.eu-gb.language-translator.watson.cloud.ibm.com/instances/96004508-c661-42d0-9215-75a7ab5b0db7"

    authenticator = IAMAuthenticator(apikey_t)
    lt = LanguageTranslatorV3(version='2018-05-01', authenticator=authenticator)
    lt.set_service_url(url_t)
    
    apikey_s = "kWqNYDvm_kLwk7YMXV-9pliFJlg1OWwQBo8E2Zujv0EQ"
    url_s = "https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/db67b916-d0dc-41c9-8054-94614e5e6eab"
    authenticator = IAMAuthenticator(apikey_s)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(url_s)

    apikey_cs = "yJ5cWiiSAIQv5EQEVCHjYHKJB0HLBNmqOBzuLUWW9mAl"
    url_cs = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/5eadba95-c1af-4ee0-9c78-dc102f4ac908"


    authenticator = IAMAuthenticator(apikey_cs)
    nlu = NaturalLanguageUnderstandingV1(version='2020-08-01', authenticator=authenticator)
    nlu.set_service_url(url_cs)

    return lt, stt, nlu

lt, stt, nlu = authentication()


def translate(language, text):
    model_id_ = 'en-es'
    if language=="spanish":
        model_id_ = 'en-es'
    if language=="korean":
        model_id_= 'en-ko'
    if language=="french":
        model_id_='en-fr'
    translation = lt.translate(text=text, model_id=model_id_).get_result()
    trans = translation['translations'][0]['translation']
    return trans


def convert_speech_to_text(file):
    res = stt.recognize(audio=file, content_type='audio/mp3', model='en-US_ShortForm_NarrowbandModel').get_result()
    text = res['results'][0]['alternatives'][0]['transcript']
    print("ttttttttttttttttttttttttttttt", text)
    return text

def check_semantic(sentence):
    response = nlu.analyze(text=sentence, features=Features(sentiment=SentimentOptions())).get_result()
    semantic = response['sentiment']['document']['label']
    return semantic


# Create your views here.

def movie_list(request):
    movie_details = Movie_detail.objects.all()
    return render(request, "movie/movie_list.html", {
        "movies": movie_details
    })

def save_to_db_(audio, movie):
    text = convert_speech_to_text(audio)
    print("**************", text)
    semantic = check_semantic(text)
    print("--------------------", semantic)
    if semantic!="violence":
        comment_instance = Comment.objects.create(movie=movie, comment=text)



def movie_page(request, movie_name):
    movie = Movie_detail.objects.get(name=movie_name)
    comments = Comment.objects.filter(movie=movie)
    comments_list = list(map(lambda x: x.comment , comments))
    if request.method=='POST':
        form = AudioForm(request.POST, request.FILES or None)
        #print("RRRRRRRRRRRRRRRRRRRR",request.POST['language'])
        #print("TTTTTTTTTTTTTTTTTTTT", request.FILES=={})
        if form.is_valid() and request.FILES!={}:
            audio = request.FILES['record']
            save_to_db_(audio, movie)
            audios = Audio_store.objects.all()
            for audio in audios:
                audio.delete()
                
            form = AudioForm()
            comments = Comment.objects.filter(movie=movie)
            comments_list = list(map(lambda x: x.comment , comments))
            return render(request, "movie/movie_page.html", {
                "movie": movie,
                "comments": comments_list,
                "form": form
                })
        else:
            # translating comments 
            language = request.POST['language']
            print("sssssss", comments_list)
            comments_list = list(map(lambda x: translate(language, x), comments_list))
            return render(request, "movie/movie_page.html", {
                "movie": movie,
                "comments": comments_list,
                "form": form
                })
    else:
        form = AudioForm()
        return render(request, "movie/movie_page.html", {
        "movie": movie,
        "comments": comments_list,
        "form" : form
        }) 
