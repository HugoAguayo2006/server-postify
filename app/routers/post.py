import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import select

from app.db.session import get_session
from app.models.comment import Comment
from app.models.images import Image
from app.models.like import Like
from app.models.post import Post
from app.schemas.comments import CommentCreate, CommentRead
from app.schemas.like import LikeCreate, LikeRead
from app.schemas.post import PostCreate, PostRead, PostReadDetails, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostRead])
async def get_posts(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Post))
    return result.scalars().all()


@router.get("/{post_id}", response_model=PostReadDetails)
async def get_post(post_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like_result = await session.execute(select(Like).where(Like.post_id == post_id))
    likes = like_result.scalars().all()

    comments_result = await session.execute(select(Comment).where(Comment.post_id == post_id))
    comments = comments_result.scalars().all()

    return PostReadDetails(
        id=post.id,
        user_id=post.user_id,
        description=post.description,
        created_at=post.created_at,
        likes=[LikeRead(**like.model_dump()) for like in likes],
        comments=[CommentRead(**comment.model_dump()) for comment in comments],
    )


@router.post("/", response_model=PostRead, status_code=201)
async def create_ser(data: PostCreate, session: AsyncSession = Depends(get_session)):
    post = Post(**data.model_dump())
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: uuid.UUID,
    data: PostUpdate,
    session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_data = data.model_dump(exclude_unset=True)
    for key, value in post_data.items():
        setattr(post, key, value)

    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await session.execute(delete(Like).where(Like.post_id == post_id))
    await session.execute(delete(Comment).where(Comment.post_id == post_id))
    await session.execute(delete(Image).where(Image.post_id == post_id))
    await session.delete(post)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{post_id}/likes", response_model=LikeRead, status_code=201)
async def add_like(
    post_id: uuid.UUID,
    data: LikeCreate,
    session: AsyncSession = Depends(get_session),
):
    if data.post_id != post_id:
        raise HTTPException(status_code=400, detail="Post ID does not match")

    post = await session.get(Post, data.post_id)

    if not post: 
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_like = await session.execute(
        select(Like).where(Like.post_id == data.post_id, Like.user_id == data.user_id)
    )


    if existing_like.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Like already exists")

    like = Like(**data.model_dump())
    session.add(like)
    await session.commit()
    await session.refresh(like)

    return LikeRead(**like.model_dump())


@router.post("/{post_id}/comments", response_model=CommentRead, status_code=201)
async def add_comment(
    post_id: uuid.UUID,
    data: CommentCreate,
    session: AsyncSession = Depends(get_session),
):
    if data.post_id != post_id:
        raise HTTPException(status_code=400, detail="Post ID does not match")

    post = await session.get(Post, post_id)

    if not post: 
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(**data.model_dump())
    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    return CommentRead(**comment.model_dump())
