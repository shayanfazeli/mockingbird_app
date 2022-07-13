from app import scheduler, cache_folderpath, scheduler, mail
from flask_mail import Message
import os
from app.libraries.io.read_write import read_pkl_gz
from app.libraries.topic_modeling.utilities import get_topic_modeling_data


@scheduler.task('interval', id='topic_modeling_request_processor', seconds=15, misfire_grace_time=600)
def topic_modeling_request_processor():
    repo_requests = os.path.join(cache_folderpath, 'requests', 'args')
    active_requests = [f for f in os.listdir(repo_requests) if f.endswith('.pkl.gz') and f.startswith('topic_modeling_')]

    if len(active_requests) == 0:
        return
    else:
        scheduler.pause()
        print("PROCESSING WORD CLOUD PROCESSOR")
        for request_filename in active_requests:
            try:
                args = read_pkl_gz(os.path.join(repo_requests, request_filename))
                _, _ = get_topic_modeling_data(**args)

                if os.path.exists(os.path.join(cache_folderpath, 'requests', 'emails', request_filename)):
                    emails = read_pkl_gz(os.path.join(cache_folderpath, 'requests', 'emails', request_filename))
                    if len(emails) > 0:
                        msg = Message("Your request is ready!",
                                      sender=("Mockingbird", "noreply@mockingbirdrefocus.com"),
                                      bcc=emails)

                        msg.body = f"""
                            Your request (id: {request_filename[:-len('.pkl.gz')]}) is done and results are ready for your review.
            
                            Args: {args}
                            """
                        from application import application
                        with application.app_context():
                            mail.send(msg)
                    os.system(f"rm {os.path.join(cache_folderpath, 'requests', 'emails', request_filename)}")
                os.system(f'rm {os.path.join(repo_requests, request_filename)}')
            except Exception as e:
                print(e)

        scheduler.resume()