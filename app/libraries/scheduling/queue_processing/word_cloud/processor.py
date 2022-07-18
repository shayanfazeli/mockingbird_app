from app import scheduler, cache_folderpath, scheduler, mail
from flask_mail import Message
import os

from app.libraries.io.read_write import read_pkl_gz
from app.libraries.word_clouds.utilities import get_word_cloud_data
from app import create_app
application = create_app()


@scheduler.task('interval', id='word_cloud_request_processor', seconds=15, misfire_grace_time=600)
def word_cloud_request_processor():
    repo_requests = os.path.join(cache_folderpath, 'requests', 'args')
    active_requests = [f for f in os.listdir(repo_requests) if f.endswith('.pkl.gz') and f.startswith('word_cloud_')]

    if len(active_requests) == 0:
        return
    else:
        scheduler.pause()
        print("PROCESSING WORD CLOUD PROCESSOR")
        for request_filename in active_requests:
            try:
                args = read_pkl_gz(os.path.join(repo_requests, request_filename))
                _, _ = get_word_cloud_data(**args)

                if os.path.exists(os.path.join(cache_folderpath, 'requests', 'emails', request_filename)):
                    emails = [e for e in read_pkl_gz(os.path.join(cache_folderpath, 'requests', 'emails', request_filename)) if '@' in e]
                    if len(emails) > 0:
                        msg = Message("Your request is ready!",
                                      sender=("Mockingbird", "noreply@mockingbirdrefocus.com"),
                                      bcc=emails)

                        msg.body = f"""
                            Your request (id: {request_filename[:-len('.pkl.gz')]}) is done and results are ready for your review.
            
                            Args: {args}
                            """
                        with application.app_context():
                            mail.send(msg)
                    os.system(f"rm {os.path.join(cache_folderpath, 'requests', 'emails', request_filename)}")
                os.system(f'rm {os.path.join(repo_requests, request_filename)}')
            except Exception as e:
                print(e)

        scheduler.resume()
