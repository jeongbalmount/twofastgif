import json
import math
import mimetypes
import ffmpeg
import random
import string
import boto3
import os
import logging

from os.path import basename, splitext

from botocore.config import Config
from django.utils.decorators import method_decorator

from config import settings

from botocore.exceptions import ClientError

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from .models import UploadURLmodel, UploadModel
from .forms import UploadFileForm, UploadURLForm
# from django.views.decorators.csrf import csrf_exempt


# csrf 쿠키를 위한 데코레이터
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FileConvert(TemplateView):
    template_name = 'index.html'
    # 처음 홈페이지 제공

# url이 아닌 파일 업로드시 사용하는 함수
def fileUpload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES) # 폼데이터를 받는 부분
        if form.is_valid():
            # 오류 메시지나 파일 url을 받고 2번째는 오류냐 아니냐를 판단
            url_list_or_message, valid_file_boolean = form.clean_uploadedFiles()
            # 폼에서 오류면 메시지 리턴 -> 파일이 1개든 2개든 상관없음
            if valid_file_boolean is False:
                error_message = {'err_message': url_list_or_message}#<----------------------------------------------
                UploadModel.objects.all().delete()#<----------------------------------------------
                return JsonResponse(data=error_message, status=400)#<----------------------------------------------
            # form데이터를 db에 저장
            print("why")
            form_save = form.save()

            # 비디오 파일이 1개 들어왔을때
            if len(url_list_or_message) == 1:
                fps_value_1 = form.cleaned_data['fps_value_1']
                scale_1 = form.cleaned_data['scaleValue_select_1']
                start_1 = form.cleaned_data['start_1']
                end_1 = form.cleaned_data['end_1']
                use_palette_1 = form.cleaned_data['use_palette_1']
                # first_url = form.cleaned_data['first_uploaded_file']
                # 저장한 폼데이터 값 중 비디오 url가져오기
                print("why")
                first_url = form_save.first_uploaded_file
                # file_one_names = first_url.name
                # s3에 저장된 비디오 url을 불러오기
                print("why")
                s3_file_url = ('https://'
                               + settings.AWS_S3_DOMAIN
                               # + settings.AWS_CLOUDFRONT_DOMAIN
                               + '/media/'
                               + first_url.name)

                url_of_mime = mimetypes.guess_type(s3_file_url)
                if url_of_mime is not 'video/mp4':
                    changed_to_mp4_video, is_changed_to_mp4 = change_to_mp4(s3_file_url)
                else:
                    is_changed_to_mp4 = False
                    changed_to_mp4_video = s3_file_url
                # 리스케일값 유효성 검사
                width_1, height_1 = define_scale(scale_1, changed_to_mp4_video)
                # 시작 시간, 끝나는 시간 유효성 검사
                start_end_valid, message_or_end, is_default_end = validate_start_end_time(changed_to_mp4_video,
                                                                                          start_1, end_1)

                # 틀리면 오류 메시지 리턴
                if start_end_valid is False:
                    error_message = {'err_message': message_or_end}
                    UploadModel.objects.all().delete()
                    return JsonResponse(data=error_message, status=400)

                # 파일 gif로 바꾸기
                gif_s3_url = make_gif(changed_to_mp4_video, fps_value_1, width_1, height_1, start_1, message_or_end,
                                      is_default_end, use_palette_1, is_changed_to_mp4)
                dict_urls = {'url_one': gif_s3_url}
                # 로컬에 남아 있는 모델 데이터 지우기
                UploadModel.objects.all().delete()
            else:   # 비디오 파일이 2개 넘어 올때
                first_url = form_save.first_uploaded_file
                second_url = form_save.second_uploaded_file
                fps_value_1 = form.cleaned_data['fps_value_1']
                fps_value_2 = form.cleaned_data['fps_value_2']
                scale_1 = form.cleaned_data['scaleValue_select_1']
                scale_2 = form.cleaned_data['scaleValue_select_2']
                start_1 = form.cleaned_data['start_1']
                end_1 = form.cleaned_data['end_1']
                start_2 = form.cleaned_data['start_2']
                end_2 = form.cleaned_data['end_2']
                use_palette_1 = form.cleaned_data['use_palette_1']
                use_palette_2 = form.cleaned_data['use_palette_2']
                # file_one_name = first_url.name
                # file_two_name = second_url.name

                s3_file_url_first = ('https://'
                                     + settings.AWS_S3_DOMAIN
                                     # + settings.AWS_CLOUDFRONT_DOMAIN+
                                     + '/media/'
                                     + first_url.name)
                s3_file_url_second = ('https://'
                                      + settings.AWS_S3_DOMAIN
                                      # + settings.AWS_CLOUDFRONT_DOMAIN
                                      + '/media/'
                                      + second_url.name)

                url_of_mime_1 = mimetypes.guess_type(s3_file_url_first)
                url_of_mime_2 = mimetypes.guess_type(s3_file_url_second)

                if url_of_mime_1 is not 'video/mp4':
                    changed_to_mp4_video_1, is_changed_to_mp4_1 = change_to_mp4(s3_file_url_first)
                else:
                    is_changed_to_mp4_1 = False
                    changed_to_mp4_video_1 = s3_file_url_first

                if url_of_mime_2 is not 'video/mp4':
                    changed_to_mp4_video_2, is_changed_to_mp4_2 = change_to_mp4(s3_file_url_second)
                    print("changed!")
                else:
                    is_changed_to_mp4_2 = False
                    changed_to_mp4_video_2 = s3_file_url_first

                width_1, height_1 = define_scale(scale_1, changed_to_mp4_video_1)
                width_2, height_2 = define_scale(scale_2, changed_to_mp4_video_2)
                start_end_valid_1, message_or_end_1, is_default_end = validate_start_end_time(changed_to_mp4_video_1,
                                                                                              start_1, end_1)
                start_end_valid_2, message_or_end_2, is_default_end = validate_start_end_time(changed_to_mp4_video_2,
                                                                                              start_2, end_2)

                if start_end_valid_1 is False or start_end_valid_2 is False:
                    error_message = {'err_message': 'overTotalLength'}
                    UploadModel.objects.all().delete()
                    return JsonResponse(data=error_message, status=400)

                gif_s3_url_first = make_gif(changed_to_mp4_video_1, fps_value_1, width_1, height_1, start_1,
                                            message_or_end_1, is_default_end, use_palette_1, is_changed_to_mp4_1)
                print("before  change 2")
                gif_s3_url_second = make_gif(changed_to_mp4_video_2, fps_value_2, width_2, height_2, start_2,
                                             message_or_end_2, is_default_end, use_palette_2, is_changed_to_mp4_2)
                dict_urls = {'url_one': gif_s3_url_first, 'url_two': gif_s3_url_second}

                UploadModel.objects.all().delete()

            return JsonResponse(data=dict_urls, status=201)
        else:
            error_message = {'err_message': 'Please refresh and use it again'}
            UploadModel.objects.all().delete()
            return JsonResponse(data=error_message, status=400)


# 비디오 파일 url이 넘어 올때
def URLupload(request):
    if request.method == 'POST':
        # 비디오파일 url과 설정 데이터가 넘어올때
        print(json.loads(request.body))
        form = UploadURLForm(json.loads(request.body))
        if form.is_valid():
            valid_url_or_error_message, valid_file_boolean = form.clean_uploadURLs()
            if valid_file_boolean is False:
                error_message = {'err_message': valid_url_or_error_message}
                UploadURLmodel.objects.all().delete()
                return JsonResponse(data=error_message, status=400)
            if len(valid_url_or_error_message) is 1:
                file_url = form.cleaned_data['uploadURL_1']
                url_scale = form.cleaned_data['URL_scaleValue_select_1']
                url_fps = form.cleaned_data['URL_fps_value_1']
                url_start = form.cleaned_data['URL_start_1']
                url_end = form.cleaned_data['URL_end_1']
                use_palette_1 = form.cleaned_data['use_palette_1']
                # save()를 통해 나오는 것은 파일 이름!
                # file_url이 model타입이기 때문에 str형식인 name사용

                url_of_mime = mimetypes.guess_type(file_url)
                if url_of_mime is not 'video/mp4':
                    changed_to_mp4_video, is_changed_to_mp4 = change_to_mp4(file_url)
                else:
                    is_changed_to_mp4 = False
                    changed_to_mp4_video = file_url

                url_width, url_height = define_scale(url_scale, changed_to_mp4_video)
                start_end_valid, URL_message_or_end, is_default_end = validate_start_end_time(changed_to_mp4_video,
                                                                                              url_start, url_end)
                if start_end_valid is False:
                    error_message = {'err_message': URL_message_or_end}
                    UploadURLmodel.objects.all().delete()
                    return JsonResponse(data=error_message, status=400)
                gif_s3_url = make_gif(changed_to_mp4_video, url_fps, url_width, url_height, url_start, URL_message_or_end,
                                      is_default_end, use_palette_1, is_changed_to_mp4)
                dict_url = {'url_one': gif_s3_url}
                UploadURLmodel.objects.all().delete()

                return JsonResponse(data=dict_url, status=201)
            else:
                file_url = form.cleaned_data['uploadURL_1']
                file_url_2 = form.cleaned_data['uploadURL_2']
                url_scale = form.cleaned_data['URL_scaleValue_select_1']
                url_scale_2 = form.cleaned_data['URL_scaleValue_select_2']
                url_fps = form.cleaned_data['URL_fps_value_1']
                url_fps_2 = form.cleaned_data['URL_fps_value_2']
                url_start = form.cleaned_data['URL_start_1']
                url_start_2 = form.cleaned_data['URL_start_2']
                url_end = form.cleaned_data['URL_end_1']
                url_end_2 = form.cleaned_data['URL_end_2']
                use_palette_1 = form.cleaned_data['use_palette_1']
                use_palette_2 = form.cleaned_data['use_palette_2']

                url_of_mime_1 = mimetypes.guess_type(file_url)
                if url_of_mime_1 is not 'video/mp4':
                    changed_to_mp4_video_1, is_changed_to_mp4_1 = change_to_mp4(file_url)
                else:
                    is_changed_to_mp4_1 = False
                    changed_to_mp4_video_1 = file_url

                url_of_mime_2 = mimetypes.guess_type(file_url_2)
                if url_of_mime_2 is not 'video/mp4':
                    changed_to_mp4_video_2, is_changed_to_mp4_2 = change_to_mp4(file_url_2)
                else:
                    is_changed_to_mp4_2 = False
                    changed_to_mp4_video_2 = file_url_2

                url_width, url_height = define_scale(url_scale, changed_to_mp4_video_1)
                url_width_2, url_height_2 = define_scale(url_scale_2, changed_to_mp4_video_2)

                start_end_valid, URL_message_or_end, is_default_end = validate_start_end_time(changed_to_mp4_video_1,
                                                                                              url_start, url_end)
                start_end_valid_2, URL_message_or_end_2, is_default_end = validate_start_end_time(changed_to_mp4_video_2,
                                                                                                  url_start_2,
                                                                                                  url_end_2)

                if start_end_valid is False or start_end_valid_2 is False:
                    error_message = {'err_message': URL_message_or_end}
                    UploadURLmodel.objects.all().delete()
                    return JsonResponse(data=error_message, status=400)

                gif_s3_url = make_gif(changed_to_mp4_video_1, url_fps, url_width, url_height, url_start,
                                      URL_message_or_end,
                                      is_default_end, use_palette_1, is_changed_to_mp4_1)
                gif_s3_url_2 = make_gif(changed_to_mp4_video_2, url_fps_2, url_width_2, url_height_2,
                                        url_start_2, URL_message_or_end_2, is_default_end, use_palette_2,
                                        is_changed_to_mp4_2)

                dict_url = {'url_one': gif_s3_url, 'url_two': gif_s3_url_2,}
                UploadURLmodel.objects.all().delete()

                return JsonResponse(data=dict_url, status=201)

    else:
        error_message = {'err_message': 'Please refresh and use it again'}
        UploadURLmodel.objects.all().delete()
        return JsonResponse(data=error_message, status=400)


def make_gif(changed_to_mp4_video, fps_value, input_width, input_height, input_start, input_end, is_default_end,
             use_palette, is_changed_to_mp4):
    # re_thing = re.compile('.+(?<=/)')
    # 파일 이름을 구성하는 난수를 위한 const변수들
    print("in makegif")
    _LENGTH = 12
    _LENGTH_2 = 15
    _MIDDLELEN = 3

    # 파일 이름 구성하는 변수들
    short_random_value = make_random_string(_MIDDLELEN)
    long_random_value = make_random_string(_LENGTH)

    # 리스케일링 된 파일의 이름, 팔레트 png 파일이름
    random_rescale_filename = make_random_string(_LENGTH_2)
    random_palette_filename = str(round(random.random() * 100000000000))

    # 비디오 파일 리스케일시 파일 확장자에 붙여줄 확장자 뽑는 과정
    # furl, file_extension = splitext(s3_file_url)

    # 변환 파일이름 구하는 변수
    out_file_name = "GIF-" + \
                    short_random_value + '-' + long_random_value + '.gif'
    # 리스케일된 비디오 파일 이름 변수
    out_edit_start_end_or_not_file_name = "start_end-" + random_rescale_filename + '.mp4'
    out_rescale_or_not_file_name = "rescale-" + random_rescale_filename + '.mp4'
    # 팔레트 이름 변수
    out_palette_name = "palette-"+random_palette_filename+'.png'
    # limit_second_per_fps = 300  # fps25-> 12sec fps15 -> 20sec fps10 -> 30sec

    # 각 fps에 맞는 제한 시간에 전체 재생시간을 맞춘다
    valid_end = limit_time_by_frame(fps_value, input_start, input_end)

    # limit_.. 함수를 통해 input_end값이 바뀌었다면 is_default..변수는 False가 되어야 한다.
    if valid_end is not input_end and is_default_end is True:
        is_default_end = False

    # 시작시간, 끝나는 시간 정해준다.
    if input_start is not 0 or is_default_end is False:
        print("if input start is not 0")
        (
            ffmpeg
            .input(changed_to_mp4_video)
            .trim(start=input_start, end=valid_end)
            .setpts('PTS-STARTPTS')
            .output(out_edit_start_end_or_not_file_name)
            .run(overwrite_output=True)
        )
    else:
        out_edit_start_end_or_not_file_name = changed_to_mp4_video

    # 기본 해상도로 설정되어 있지 않으면 리스케일한다.
    if input_width is not -1 or input_height is not -1:
        print("if it is not default scale")
        (
            ffmpeg
            .input(out_edit_start_end_or_not_file_name)
            .filter('scale', input_width, input_height)
            .output('{}'.format(out_rescale_or_not_file_name))
            .run(overwrite_output=True)
        )
    else:
        out_rescale_or_not_file_name = out_edit_start_end_or_not_file_name

    if use_palette is 1:
        print("make palette")
        # 움짤의 선명도를 높이기 위해 palette생성
        (
            ffmpeg
            .input(out_rescale_or_not_file_name)
            .filter(filter_name='palettegen', stats_mode='full')
            .output('{}'.format(out_palette_name))
            .run(overwrite_output=True)
        )
        # 비디오 파일을 움짤로 바꿀때 팔레트와 함성하는 작업
        (
            ffmpeg.filter(
                [
                    ffmpeg.input(out_rescale_or_not_file_name, format='mp4'),
                    ffmpeg.input('{}'.format(out_palette_name))
                ],
                filter_name='paletteuse',
                dither='heckbert',
                new='False',
            )
            .filter('fps', fps=fps_value)# fps적용하기
            .output('{}'.format(out_file_name)) # crf값을 올리고 preset을 ultrafast로 해 변환시간 줄임 , crf=51, preset='ultrafast'
            .run(overwrite_output=True)
        )
    else:
        (
            ffmpeg
            .input(out_rescale_or_not_file_name)
            .filter('fps', fps=fps_value)
            .output('{}'.format(out_file_name))
            .run(overwrite_output=True)
        )

    # s3 사용가능하게 만들기
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'), aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    # s3에 업로드 하기
    with open('{}'.format(out_file_name), "rb") as f:
        s3.upload_fileobj(f, "fileconvertstorage", "gif_file/{out_file_name}".format(out_file_name=out_file_name))
    # 로컬에 남아 있는 파일들 지우기
    if use_palette is 1:
        os.remove('{}'.format(out_palette_name))
    os.remove('{}'.format(out_file_name))
    # mp4로 변환했던 파일 삭제
    if is_changed_to_mp4 is True:
        os.remove('{}'.format(changed_to_mp4_video))
    # 너비나 높이 중 하나라도 수정되었다면 리스케일링 된 비디오 파일 지우기
    if input_width is not -1 or input_height is not -1:
        os.remove('{}'.format(out_rescale_or_not_file_name))

    if input_start is not 0 or is_default_end is False:
        os.remove('{}'.format(out_edit_start_end_or_not_file_name))

    bucket_name = "fileconvertstorage"
    object_name = "gif_file/{out_file_name}".format(out_file_name=out_file_name)
    # presigned_url 만들기
    # client = boto3.client('cloudfront')
    # print(client)
    # presigned_for_cloud = client.presigned_url(ClientMethod='get_object',
    #                                      Params={'Bucket': bucket_name,
    #                                              'Key': object_name},
    #                                      ExpiresIn=120)
    # print(presigned_for_cloud)
    presigned_url = create_presigned_url(s3, bucket_name, object_name)

    if presigned_url is None:
        return None

    return presigned_url


def change_to_mp4(will_change_video):
    random_name = make_random_string(10)
    changed_file_name = 'changed_file_name' + random_name + '.mp4'
    print("now change to mp4")
    (
        ffmpeg
        .input(will_change_video)
        .setpts('PTS-STARTPTS')
        .output(changed_file_name, format='mp4')
        .run(overwrite_output=True)
    )
    is_changed_to_mp4 = True
    return changed_file_name, is_changed_to_mp4


# 시간이 지나면 사라지는 url을 만드는 함수
def create_presigned_url(s3, bucket_name, object_name, expiration=120):
    try:
        response = s3.generate_presigned_url(ClientMethod='get_object',
                                         Params={'Bucket': bucket_name,
                                                 'Key': object_name},
                                         ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    return response


# 랜덤한 숫자+문자를 만들어낸다.
def make_random_string(length):
    result = ""
    string_pool = string.ascii_letters + string.digits

    for i in range(length):
        result += random.choice(string_pool)

    return result


# 해상도를 결정하는 함수
def define_scale(input_scale, input_file_url):
    width = -1
    height = -1

    file_width = ffmpeg.probe(input_file_url)['streams'][0]['width']
    file_height = ffmpeg.probe(input_file_url)['streams'][0]['height']

    if input_scale == "가로:600px":
        width = 600
        height = -2
    elif input_scale == "가로:480px":
        width = 480
        height = -2
    elif input_scale == "세로:480px":
        width = -2
        height = 480
    elif input_scale == "세로:320px":
        width = -2
        height = 320
    else:
        if file_width > 600:
            width = 600
            height = -2
            return width, height

        if file_height > 1200:
            height = 1200
            width = -2
            return width, height

    return width, height


# 전체 동영상 길이를 넘지만 않으면 된다. 프레임으로 제한 주는 것은 밑 함수가 담당한다.
def validate_start_end_time(input_file_url, input_start, input_end):
    file_url = input_file_url
    is_default_end = False
    duration = ffmpeg.probe(file_url)['format']['duration']
    duration = float(duration)
    isinput_end_default = math.isclose(input_end, -1.0)

    if isinput_end_default is True and duration > input_start:
        is_default_end = True
        return True, duration, is_default_end

    elif input_start > duration or input_end > duration:
        error_message = 'overTotalLength'
        return False, error_message, is_default_end

    else:
        return True, input_end, is_default_end


# 프레임 별로 limit초를 나누어 제한한다.
def limit_time_by_frame(fps_value, input_start, input_end):

    time_value = input_end - input_start
    if fps_value is 25:
        if time_value > 12:
            input_end = input_start + 12
            return input_end
        else:
            return input_end
    elif fps_value is 15:
        if time_value > 20:
            input_end = input_start + 20
            return input_end
        else:
            return input_end
    else:
        if time_value > 30:
            input_end = input_start + 30
            return input_end
        else:
            return input_end





