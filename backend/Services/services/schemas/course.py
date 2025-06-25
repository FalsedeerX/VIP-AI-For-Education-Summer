from typing import Any, Dict, List
from pydantic import BaseModel


CourseContent = dict[str, list[int]]


class NewCourse(BaseModel):
	course_code: str
	course_title: str


class CourseInfo(BaseModel):
	course_id: int

CourseFolder = List[Dict[str, Any]]