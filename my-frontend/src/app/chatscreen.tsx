"use client";

import React, { useState, useEffect, useCallback, Fragment } from "react";
import { useRouter } from "next/navigation";
import { getJson, postJson } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
  Sidebar,
  SidebarProvider,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Plus, MessageSquare, FolderPlus } from "lucide-react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

interface Course {
  course_id: number;
  title: string;
}

interface Folder {
  folder_id: number;
  title: string;
}

export default function ChatScreen() {
  const { userId, loading } = useAuth();
  const router = useRouter();

  const [courses, setCourses] = useState<Course[]>([]);
  const [foldersByCourse, setFoldersByCourse] = useState<
    Record<number, Folder[]>
  >({});
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [showAddCourse, setShowAddCourse] = useState(false);
  const [newCourseCode, setNewCourseCode] = useState("");

  // Redirect if not authenticated
  if (loading) return null;
  if (!userId) {
    router.replace("/login");
    return null;
  }

  // Fetch courses
  const loadCourses = useCallback(async () => {
    try {
      const data = await getJson<Course[]>("/users/getcourses", true);
      setCourses(data);
    } catch (err) {
      console.error("Failed to load courses", err);
    }
  }, []);

  // Fetch folders for a course
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

  const handleSelectCourse = (courseId: number) => {
    setSelectedCourse(courseId);
    setSelectedFolder(null);
    loadFolders(courseId);
  };

  const handleSelectFolder = (folderId: number) => {
    setSelectedFolder(folderId);
  };

  const handleJoinCourse = async () => {
    if (!newCourseCode.trim()) return;
    try {
      await postJson<boolean>(
        "/users/joincourse",
        { course_code: newCourseCode },
        true
      );
      setNewCourseCode("");
      setShowAddCourse(false);
      loadCourses();
    } catch (err) {
      console.error("Error joining course", err);
    }
  };

  const handleNewChat = () => {
    // TODO: navigate to or open a new chat under selectedFolder
  };

  return (
    <SidebarProvider>
      <div className="flex h-screen">
        <Sidebar className="w-64 border-r bg-background">
          <SidebarHeader>
            <Dialog open={showAddCourse} onOpenChange={setShowAddCourse}>
              <DialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full flex items-center justify-center bg-[var(--color-purdue-gold)] hover:bg-[var(--color-purdue-black)] text-[var(--color-purdue-black)] font-semibold"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Join Course
                </Button>
              </DialogTrigger>

              <DialogContent className="bg-[var(--color-purdue-gold)] text-[var(--color-purdue-black)]">
                <DialogHeader>
                  <DialogTitle>Join a Course</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <Input
                    placeholder="Course Code"
                    value={newCourseCode}
                    onChange={(e) => setNewCourseCode(e.target.value)}
                  />
                </div>
                <DialogFooter>
                  <Button
                    onClick={handleJoinCourse}
                    className="w-full bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold"
                  >
                    <FolderPlus className="mr-2 h-4 w-4" />
                    Join
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </SidebarHeader>

          <SidebarContent>
            <SidebarMenu>
              {courses.map((course) => (
                <Fragment key={course.course_id}>
                  <SidebarMenuItem
                    onClick={() => handleSelectCourse(course.course_id)}
                    className={
                      selectedCourse === course.course_id
                        ? "bg-muted font-bold"
                        : ""
                    }
                  >
                    {course.title}
                  </SidebarMenuItem>

                  {selectedCourse === course.course_id && (
                    <SidebarMenuSub>
                      {(foldersByCourse[course.course_id] || []).map(
                        (folder) => (
                          <SidebarMenuSubItem key={folder.folder_id}>
                            <SidebarMenuSubButton
                              isActive={selectedFolder === folder.folder_id}
                              onClick={() =>
                                handleSelectFolder(folder.folder_id)
                              }
                            >
                              {folder.title}
                            </SidebarMenuSubButton>
                          </SidebarMenuSubItem>
                        )
                      )}

                      <SidebarMenuSubItem>
                        <SidebarMenuSubButton onClick={handleNewChat}>
                          <MessageSquare className="mr-2 h-4 w-4" />
                          New Chat
                        </SidebarMenuSubButton>
                      </SidebarMenuSubItem>
                    </SidebarMenuSub>
                  )}
                </Fragment>
              ))}
            </SidebarMenu>
          </SidebarContent>

          <SidebarFooter>
            {/* add any footer items (settings, logout, etc.) here */}
          </SidebarFooter>
        </Sidebar>

        <main className="flex-1 overflow-auto">
          {/* Render chat window here, based on selectedFolder */}
        </main>
      </div>
    </SidebarProvider>
  );
}
