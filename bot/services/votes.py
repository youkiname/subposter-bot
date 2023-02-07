from models import Vote, VoteTypes


def get_post_likes_amount(post_id: int) -> int:
    return Vote.select().where(Vote.post_id == post_id, Vote.type == VoteTypes.like).count()


def get_post_dislikes_amount(post_id: int) -> int:
    return Vote.select().where(Vote.post_id == post_id, Vote.type == VoteTypes.dislike).count()
