from dotenv import load_dotenv
from supplement_review_crew.crew import SupplementReviewCrew

load_dotenv()


def supplement_review():
    inputs = {
        'topic': 'Pineal XT',
    }
    SupplementReviewCrew().crew().kickoff(inputs=inputs)


def run():
    supplement_review()


if __name__ == '--main__':
    run()
