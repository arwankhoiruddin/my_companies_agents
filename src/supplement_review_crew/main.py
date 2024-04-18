from dotenv import load_dotenv
from supplement_review_crew.crew import SupplementReviewCrew

load_dotenv()


def supplement_review():
    inputs = {
        'topic': 'Pineal XT',
    }
    result = SupplementReviewCrew().crew().kickoff(inputs=inputs)
    print(result)


def run():
    supplement_review()


if __name__ == '--main__':
    run()
