from app import scheduler, cache_folderpath, scheduler, mail
from flask_mail import Message
import os

from app.libraries.io.read_write import read_pkl_gz
from app.libraries.word_frequency.utilities import get_word_frequency_data
from app.libraries.utilities.logging import get_logger
from app import create_app
application = create_app()
logger = get_logger(__name__)


@scheduler.task('interval', id='word_frequency_request_processor', seconds=15, misfire_grace_time=None, max_instances=1)
def word_frequency_request_processor():
    repo_requests = os.path.join(cache_folderpath, 'requests', 'args')
    active_requests = [f for f in os.listdir(repo_requests) if f.endswith('.pkl.gz') and f.startswith('word_frequency_')]

    if len(active_requests) == 0:
        return
    else:
        scheduler.pause()
        for request_filename in active_requests:
            try:
                args = read_pkl_gz(os.path.join(repo_requests, request_filename))
                _ = get_word_frequency_data(**args)


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
                        logger.info("before this import.")
                        with application.app_context():
                            mail.send(msg)
                            logger.info("email sent.")
                    os.system(f"rm {os.path.join(cache_folderpath, 'requests', 'emails', request_filename)}")
                os.system(f'rm {os.path.join(repo_requests, request_filename)}')
            except Exception as e:
                logger.warning(f"EXCEPTION OCCURRED -> details:\n\t->[{e}]\n\n")

        scheduler.resume()
