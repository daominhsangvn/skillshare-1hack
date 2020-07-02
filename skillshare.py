import requests, json, sys, re, os, re, shutil
from slugify import slugify

class Skillshare(object):

    def __init__(
        self,
        cookie,
        downloaded_history_file_path,
        download_path=os.environ.get('FILE_PATH', './Skillshare'),
        pk='BCpkADawqM2OOcM6njnM7hf9EaK6lIFlqiXB0iWjqGWUQjU7R8965xUvIQNqdQbnDTLz0IAO7E6Ir2rIbXJtFdzrGtitoee0n1XXRliD-RH9A-svuvNW9qgo3Bh34HEZjXjG4Nml4iyz3KqF',
        brightcove_account_id=3695997568001,
    ):
        self.downloaded_history_file_path = downloaded_history_file_path
        self.cookie = cookie.strip().strip('"')
        self.download_path = download_path
        self.pk = pk.strip()
        self.brightcove_account_id = brightcove_account_id
        self.pythonversion = 3 if sys.version_info >= (3, 0) else 2

    def is_unicode_string(self, string):
        if (self.pythonversion == 3 and isinstance(string, str)) or (self.pythonversion == 2 and isinstance(string, unicode)):
            return True

        else:
            return False

    def is_downloaded(self, class_id):
        downloaded_history_file = open(self.downloaded_history_file_path, "r") 
        downloaded_list = downloaded_history_file.readlines()
        downloaded_history_file.close()
        return class_id + '\n' in downloaded_list

    def update_downloaded(self, class_id):
        downloaded_history_file = open(self.downloaded_history_file_path, "a") 
        downloaded_history_file.write(class_id + '\n')
        downloaded_history_file.close()

    def download_course_skills(self, url):
        page_request = requests.get(url, allow_redirects=True)
        skill_lines = re.findall(r"href\=\"\/search\?query\=(.*)\&amp.*?\"", page_request.content.decode('utf-8'))
        return skill_lines

    def download_course_by_url(self, url, target_folder):
        m = re.match('https://www.skillshare.com/classes/(.*?)/(\\d+)', url)
        assert m, 'Failed to parse class ID from URL'
        self.download_course_by_class_id(m.group(2), m.group(1), target_folder, url)

    def download_course_by_class_id(self, class_id, class_name, target_folder, url):
        is_course_downloaded = self.is_downloaded(class_id)
        if is_course_downloaded:
            print('Downloaded Already!')
            return
        course_skills = self.download_course_skills(url)
        data = self.fetch_course_data_by_class_id(class_id=class_id)
        teacher_name = None
        if 'vanity_username' in data['_embedded']['teacher']:
            teacher_name = data['_embedded']['teacher']['vanity_username']
        if not teacher_name:
            teacher_name = data['_embedded']['teacher']['full_name']
        assert teacher_name, 'Failed to read teacher name from data'
        if self.is_unicode_string(teacher_name):
            teacher_name = teacher_name.encode('ascii', 'replace')
        title = data['title']
        title = title.replace(":", "_")
        title = title.replace("|", "_")
        # Prepend class id
        title = "("+class_id+") " + title

        # Append course skills
        skills_str = ""
        for skill in course_skills:
            skills_str = skills_str + "("+skill+")"
        if len(course_skills) > 0:
            title = title + " -- Skills" + skills_str

        #print(title)
        #if self.is_unicode_string(title):
        #    title = title.encode('ascii', 'replace')
        #print(title)
        base_path = os.path.abspath(os.path.join(self.download_path, title)).rstrip('/')
        target_path = '{target_folder}/{title}'.format(target_folder=target_folder, title=title)
        
        # Clean up
        if os.path.exists(base_path):
            shutil.rmtree(base_path)
            
        # Init folder
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
        for u in data['_embedded']['units']['_embedded']['units']:
            for s in u['_embedded']['sessions']['_embedded']['sessions']:
                video_id = None
                if 'video_hashed_id' in s:
                    if s['video_hashed_id']:
                        video_id = s['video_hashed_id'].split(':')[1]
                    assert video_id, 'Failed to read video ID from data'
                    s_title = s['title']
                    if self.is_unicode_string(s_title):
                        s_title = s_title.encode('ascii', 'replace')
                    file_name = '{} - {}'.format(str(s['index'] + 1).zfill(2), slugify(s_title))
                    self.download_video(fpath='{base_path}/{session}.mp4'.format(base_path=base_path,
                      session=file_name),
                      spath='{base_path}/{session}.vtt'.format(base_path=base_path, session=file_name),
                      srtpath='{base_path}/{session}.srt'.format(base_path=base_path, session=file_name),
                      video_id=video_id,
                      file_name=file_name)
                    print('')

        # move files to target folder
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        print("* Moving files from " + base_path + " to " + target_folder)
        shutil.move(base_path, target_folder)
        self.update_downloaded(class_id)

    def fetch_course_data_by_class_id(self, class_id):
        res = requests.get(url=('https://api.skillshare.com/classes/{}'.format(class_id)),
          headers={'Accept':'application/vnd.skillshare.class+json;,version=0.8',
         'User-Agent':'Skillshare/4.1.1; Android 5.1.1',
         'Host':'api.skillshare.com',
         'cookie':self.cookie})
        assert res.status_code == 200, 'Fetch error, code == {}'.format(res.status_code)
        return res.json()

    def download_video(self, fpath, spath, srtpath, video_id, file_name):
        meta_url = 'https://edge.api.brightcove.com/playback/v1/accounts/{account_id}/videos/{video_id}'.format(account_id=(self.brightcove_account_id),
          video_id=video_id)
        meta_res = requests.get(meta_url,
          headers={'Accept':'application/json;pk={}'.format(self.pk),
         'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
         'Origin':'https://www.skillshare.com'})
        
        if(meta_res.status_code == 200):
            sub_dl_url = None

            # Video DL
            for x in meta_res.json()['sources']:
                if 'container' in x:
                    if x['container'] == 'MP4' and 'src' in x:
                        dl_url = x['src']
                        break

            # Subtitle DL
            for x in meta_res.json()['text_tracks']:
                if 'srclang' in x and x['srclang'] == 'en':
                    sub_dl_url=x['src']
                    break

            print('* Downloading Lession ' + file_name)
            if os.path.exists(fpath):
                print('>> skipping...')
            else:
                with open(fpath, 'wb') as (f):
                    response = requests.get(dl_url, allow_redirects=True, stream=True)
                    total_length = response.headers.get('content-length')
                    if not total_length:
                        f.write(response.content)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        for data in response.iter_content(chunk_size=4096):
                            dl += len(data)
                            f.write(data)
                            done = int(50 * dl / total_length)
                            sys.stdout.write('\r[%s%s]' % ('=' * done, ' ' * (50 - done)))
                            sys.stdout.flush()
                        print('')

            if bool(sub_dl_url):
                print('* Downloading Subtitle...')
                if os.path.exists(srtpath):
                    print('>> skipping...')
                else:
                    with open(spath, 'wb') as (f):
                        sub_response=requests.get(sub_dl_url, stream=True)
                        sub_total_length=sub_response.headers.get('content-length')
                        if not sub_total_length:
                            f.write(sub_response.content)
                        else:
                            sub_dl=0
                            sub_total_length=int(sub_total_length)
                            for data in sub_response.iter_content(chunk_size=4096):
                                sub_dl += len(data)
                                f.write(data)
                                sub_done=int(50 * sub_dl / sub_total_length)
                                sys.stdout.write('\r[%s%s]' %
                                                 ('=' * sub_done, ' ' * (50 - sub_done)))
                                sys.stdout.flush()
                            print('')

                    print('* Converting Subtitle...')
                    with open(spath, 'r') as subtitle_file:
                        subtitle_data = subtitle_file.read()
                        subtitle_data = re.sub(r"WEBVTT\n", "", subtitle_data)
                        subtitle_data = re.sub(r"X-TIMESTAMP-MAP.*\n", "", subtitle_data)
                        subtitle_data = re.sub(r"(\d\d):(\d\d):(\d\d)\.(\d+)", r"\1:\2:\3,\4", subtitle_data)
                        sub_lines = re.findall(r"00.*", subtitle_data)
                        li = 1
                        for l in sub_lines:
                            subtitle_data = subtitle_data.replace(l, str(li) + "\n" + l)
                            li = li + 1
                        sf = open(srtpath, "w")
                        sf.write(subtitle_data)
                        sf.close()
                    os.remove(spath)
            print('Done!')
