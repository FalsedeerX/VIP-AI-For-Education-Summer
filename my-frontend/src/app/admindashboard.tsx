"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getJson, postJson } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Trash2, FolderPlus } from "lucide-react";

interface Course {
  course_id: number;
  title: string;
}

interface Folder {
  folder_label: string;
  folder_id: number;
}

export default function AdminDashboard() {
  const { userId, admin, loading } = useAuth();
  const router = useRouter();

  // Guard
  if (loading) return null;
  if (!userId || !admin) {
    router.replace("/login");
    return null;
  }

  // State
  const [courses, setCourses] = useState<Course[]>([]);
  const [openCourseId, setOpenCourseId] = useState<string | undefined>(
    undefined
  );
  const [foldersByCourse, setFoldersByCourse] = useState<{
    [key: number]: Folder[];
  }>({});
  const [newFolderNames, setNewFolderNames] = useState<{
    [key: number]: string;
  }>({});
  const [newCourseCode, setNewCourseCode] = useState("");
  const [newCourseTitle, setNewCourseTitle] = useState("");

  // Load courses
  const loadCourses = useCallback(async () => {
    try {
      const data = await getJson<Course[]>("/users/getcourses", true);
      setCourses(data);
    } catch (err) {
      console.error("Failed to load courses", err);
    }
  }, []);

  // Load folders for a given course
  const loadFolders = async (courseId: number) => {
    try {
      const data = await postJson<Folder[]>(
        `/courses/get`,
        { course_id: courseId },
        true
      );
      setFoldersByCourse((prev) => ({ ...prev, [courseId]: data }));
    } catch (err) {
      console.error(`Failed to load folders for course ${courseId}`, err);
    }
  };

  // Effect: load courses on mount
  useEffect(() => {
    loadCourses();
  }, [loadCourses]);

  // Accordion change: fetch folders when opening
  const handleAccordionChange = (value: string) => {
    setOpenCourseId(value);
    const id = Number(value);
    if (value && !foldersByCourse[id]) {
      loadFolders(id);
    }
  };

  // Create new course
  const handleCreateCourse = async () => {
    if (!newCourseCode.trim() || !newCourseTitle.trim()) return;
    try {
      await postJson<number>(
        "/courses/create",
        { course_code: newCourseCode, course_title: newCourseTitle },
        true
      );
      await postJson<boolean>(
        "/users/joincourse",
        { course_code: newCourseCode },
        true
      );
      setNewCourseCode("");
      setNewCourseTitle("");
      loadCourses();
    } catch (err) {
      console.error("Error creating course", err);
    }
  };

  // Delete handlers
  const handleDeleteCourse = async (courseId: number) => {
    if (!confirm("Really delete this course?")) return;
    try {
      await postJson("/courses/delete", { course_id: courseId }, true);
      loadCourses();
    } catch (err) {
      console.error(`Failed to delete course ${courseId}`, err);
    }
  };

  const handleDeleteFolder = async (courseId: number, folderId: number) => {
    if (!confirm("Really delete this folder?")) return;
    try {
      await postJson("/folders/delete", { folder_id: folderId }, true);
      loadFolders(courseId);
    } catch (err) {
      console.error(`Failed to delete folder ${folderId}`, err);
    }
  };

  // Add folder
  const handleAddFolder = async (courseId: number) => {
    const name = newFolderNames[courseId]?.trim();
    if (!name) return;
    try {
      await postJson(
        "/folders/create",
        { folder_name: name, course_id: courseId },
        true
      );
      setNewFolderNames((prev) => ({ ...prev, [courseId]: "" }));
      loadFolders(courseId);
    } catch (err) {
      console.error(`Error creating folder for course ${courseId}`, err);
    }
  };

  return (
    <div className="p-8 space-y-8">
      <h1 className="text-4xl font-bold text-[var(--color-purdue-gold)]">
        Admin Dashboard
      </h1>

      <Card>
        <CardHeader>
          <CardTitle>Your Courses & Folders</CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion
            type="single"
            collapsible
            value={openCourseId}
            onValueChange={handleAccordionChange}
            className="bg-[var(--color-purdue-gold)] hover:opacity-90 text-[var(--color-purdue-)] rounded-lg shadow-lg text-[var(--color-purdue-black)]"
          >
            {courses.map((c) => (
              <AccordionItem value={c.course_id.toString()} key={c.course_id}>
                <AccordionTrigger className="flex justify-between">
                  <text className="text-[var(--color-purdue-black)] font-semibold text-lg ml-4">
                    {c.title}
                  </text>
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteCourse(c.course_id);
                    }}
                  >
                    <Trash2
                      className="h-4 w-4 text-[var(--color-purdue-black)]"
                      strokeWidth={2.5}
                    />
                  </Button>
                </AccordionTrigger>
                <AccordionContent className="space-y-4">
                  <ul className="space-y-2">
                    {foldersByCourse[c.course_id]?.length ? (
                      foldersByCourse[c.course_id].map((f) => (
                        <li
                          key={f.folder_id}
                          className="flex justify-between items-center"
                        >
                          <text className="text-[var(--color-purdue-black)] ml-2">
                            {f.folder_label}
                          </text>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() =>
                              handleDeleteFolder(c.course_id, f.folder_id)
                            }
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </li>
                      ))
                    ) : (
                      <p className="italic text-gray-500 ml-2 mb-2">
                        No folders yet.
                      </p>
                    )}
                  </ul>
                  <div className="flex space-x-2 items-center ">
                    <Input
                      placeholder="New folder name"
                      value={newFolderNames[c.course_id] || ""}
                      onChange={(e) =>
                        setNewFolderNames((prev) => ({
                          ...prev,
                          [c.course_id]: e.target.value,
                        }))
                      }
                      className="flex-1 ml-2"
                    />
                    <Button
                      onClick={() => handleAddFolder(c.course_id)}
                      className="bg-[var(--color-purdue-brown)] hover:opacity-90 text-[var(--color-purdue-black)] mr-2"
                    >
                      <FolderPlus className="mr-2 h-4 w-4" />
                      Add Folder
                    </Button>
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>

      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>Create New Course</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Course Code"
            value={newCourseCode}
            onChange={(e) => setNewCourseCode(e.target.value)}
          />
          <Input
            placeholder="Course Title"
            value={newCourseTitle}
            onChange={(e) => setNewCourseTitle(e.target.value)}
          />
          <Button
            onClick={handleCreateCourse}
            className="w-full bg-[var(--color-purdue-gold)] hover:opacity-90 text-[var(--color-purdue-black)]"
          >
            <FolderPlus className="mr-2 h-4 w-4" />
            Create & Join
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
