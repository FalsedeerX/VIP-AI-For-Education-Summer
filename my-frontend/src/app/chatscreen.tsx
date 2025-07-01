"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getJson } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarMenuItem,
  SidebarGroup,
  SidebarProvider,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Plus, MessageSquare } from "lucide-react";

interface Course {
  course_id: number;
  title: string;
}

interface Folder {
  folder_id: number;
  title: string;
}

export default function ChatScreen() {
  const { userId, admin, loading } = useAuth();
  const router = useRouter();
  const [courses, setCourses] = useState<Course[]>([]);
  const [foldersByCourse, setFoldersByCourse] = useState<
    Record<number, Folder[]>
  >({});
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);

  // Auth guard
  if (loading) return null;
  if (!userId) {
    router.replace("/login");
    return null;
  }

  // Load courses
  const loadCourses = useCallback(async () => {
    try {
      const data = await getJson<Course[]>("/users/getcourses", true);
      setCourses(data);
    } catch (err) {
      console.error("Failed to load courses", err);
    }
  }, []);

  // Load folders for a course
  const loadFolders = useCallback(
    async (courseId: number) => {
      if (foldersByCourse[courseId]) return;
      try {
        const data = await getJson<Folder[]>(
          `/courses/${courseId}/folders`,
          true
        );
        setFoldersByCourse((prev) => ({ ...prev, [courseId]: data }));
      } catch (err) {
        console.error(`Failed to load folders for course ${courseId}`, err);
      }
    },
    [foldersByCourse]
  );

  useEffect(() => {
    loadCourses();
  }, [loadCourses]);

  // Handlers
  const handleSelectCourse = (courseId: number) => {
    setSelectedCourse(courseId);
    setSelectedFolder(null);
    loadFolders(courseId);
  };

  const handleSelectFolder = (folderId: number) => {
    setSelectedFolder(folderId);
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen">
        <Sidebar className="w-64 border-r">
          <SidebarHeader className="px-4 py-3">
            <Button
              variant="ghost"
              size="sm"
              className="w-full flex items-center justify-center"
              onClick={() => {
                /* open add course modal */
              }}
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Course
            </Button>
          </SidebarHeader>

          <SidebarContent>
            {courses.map((course) => (
              <SidebarGroup
                key={course.course_id}
                title={course.title}
                onToggle={() => handleSelectCourse(course.course_id)}
              >
                {(foldersByCourse[course.course_id] || []).map((folder) => (
                  <SidebarMenuItem
                    key={folder.folder_id}
                    onClick={() => handleSelectFolder(folder.folder_id)}
                    className={
                      selectedFolder === folder.folder_id ? "bg-muted" : ""
                    }
                  >
                    {folder.title}
                  </SidebarMenuItem>
                ))}

                {selectedCourse === course.course_id && (
                  <SidebarMenuItem
                    className="mt-2"
                    onClick={() => {
                      /* open create chat modal */
                    }}
                  >
                    <MessageSquare className="mr-2 h-4 w-4" />
                    New Chat
                  </SidebarMenuItem>
                )}
              </SidebarGroup>
            ))}
          </SidebarContent>

          <SidebarFooter className="px-4 py-3">
            <Button
              variant="ghost"
              size="sm"
              className="w-full flex items-center justify-center"
              onClick={() => {
                /* open settings modal */
              }}
            >
              Settings
            </Button>
          </SidebarFooter>
        </Sidebar>

        <main className="flex-1 overflow-auto"></main>
      </div>
    </SidebarProvider>
  );
}
