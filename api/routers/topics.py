# api/routers/topics.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from api.deps import get_db
from api.models import Topic, ErrorHotspot, Student
from api.schemas import TopicOut, HeatmapUpdate, HeatmapOut
from api.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TopicOut])
def get_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).all()
    return topics

@router.post("/heatmap", response_model=HeatmapOut)
def update_heatmap(
    heatmap_data: HeatmapUpdate,
    student_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Validate student ownership
    student = db.query(Student).filter(Student.id == student_id, Student.tutor_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not accessible")

    topic = db.query(Topic).filter(Topic.id == heatmap_data.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    hotspot = db.query(ErrorHotspot).filter(
        ErrorHotspot.student_id == student_id,
        ErrorHotspot.topic_id == heatmap_data.topic_id
    ).first()

    if not hotspot:
        hotspot = ErrorHotspot(
            student_id=student_id,
            topic_id=heatmap_data.topic_id,
            heat=max(0, heatmap_data.delta) # Ensure non-negative initial heat
        )
        db.add(hotspot)
    else:
        new_heat = hotspot.heat + heatmap_data.delta
        hotspot.heat = max(0, new_heat) # Ensure heat doesn't go below 0

    db.commit()
    db.refresh(hotspot)
    return HeatmapOut(topic_id=hotspot.topic_id, heat=hotspot.heat)

@router.get("/heatmap/{student_id}", response_model=List[HeatmapOut])
def get_heatmap(student_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Validate student ownership
    student = db.query(Student).filter(Student.id == student_id, Student.tutor_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found or not accessible")

    hotspots = db.query(ErrorHotspot).filter(ErrorHotspot.student_id == student_id).all()
    return [HeatmapOut(topic_id=h.topic_id, heat=h.heat) for h in hotspots]