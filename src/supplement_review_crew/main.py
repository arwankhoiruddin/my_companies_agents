from dotenv import load_dotenv
from supplement_review_crew.crew import SupplementReviewCrew

load_dotenv()


def run():
    inputs = {
        'topic': 'Pineal XT',
    }
    SupplementReviewCrew().crew().kickoff(inputs=inputs)


if __name__ == '--main__':
    run()
