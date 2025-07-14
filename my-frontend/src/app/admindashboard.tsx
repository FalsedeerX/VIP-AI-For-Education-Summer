"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getJson, postJson, deleteJson } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
  Accordion,
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from "@/components/ui/accordion";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardDescription,
} from "@/components/ui/card";
import { Trash2, FolderPlus, Plus, Upload } from "lucide-react";

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
  const [deleteCourseId, setDeleteCourseId] = useState<number | null>(null);
  const [deleteFolderId, setDeleteFolderId] = useState<number | null>(null);
  const [addFileFolderId, setAddFileFolderId] = useState<number | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

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
    setDeleteCourseId(null);
    try {
      await deleteJson("/courses/delete", { course_id: courseId }, true);
      loadCourses();
    } catch (err) {
      console.error(`Failed to delete course ${courseId}`, err);
    }
  };

  const handleDeleteFolder = async (courseId: number, folderId: number) => {
    setDeleteFolderId(null);
    try {
      await deleteJson("/folders/delete", { folder_id: folderId }, true);
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setSelectedFile(file);
  };

  // Handler for upload form submit
  const handleUploadSubmit = async (
    e: React.FormEvent<HTMLFormElement>,
    folderId: number
  ) => {
    e.preventDefault();
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("folder_id", folderId.toString());

    const res = await fetch("/folders/upload", {
      method: "POST",
      body: formData,
      credentials: "include",
    });
    if (!res.ok) throw new Error("Upload failed");

    setSelectedFile(null);
    setAddFileFolderId(null);
    await loadFolders(folderId);
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
                  <span className="text-[var(--color-purdue-black)] font-semibold text-lg ml-4">
                    {c.title}
                  </span>
                  <Dialog
                    open={deleteCourseId === c.course_id}
                    onOpenChange={(open) =>
                      setDeleteCourseId(open ? c.course_id : null)
                    }
                  >
                    <DialogTrigger asChild>
                      <Button size="icon" variant="ghost">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-[var(--color-purdue-gold)] text-[var(--color-purdue-black)]">
                      <DialogHeader>
                        <DialogTitle className="font-semibold">
                          Delete Course
                        </DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <p>
                          Are you sure you want to delete the course
                          <strong> {c.title}</strong>?
                        </p>
                        <p className="text-red-600 font-semibold">
                          This action cannot be undone.
                        </p>
                      </div>
                      <DialogFooter>
                        <Button
                          onClick={() => {
                            handleDeleteCourse(c.course_id);
                            setDeleteCourseId(null); // close after deleting
                          }}
                          className="w-full bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </AccordionTrigger>
                <AccordionContent className="space-y-4">
                  <ul className="space-y-2">
                    {foldersByCourse[c.course_id]?.length ? (
                      foldersByCourse[c.course_id].map((f) => (
                        <li
                          key={f.folder_id}
                          className="flex justify-between items-center"
                        >
                          <span className="text-[var(--color-purdue-black)] ml-3">
                            {f.folder_label}
                          </span>
                          <div>
                            <Dialog
                              open={deleteFolderId === f.folder_id}
                              onOpenChange={(open) =>
                                setDeleteFolderId(open ? f.folder_id : null)
                              }
                            >
                              <DialogTrigger asChild>
                                <Button size="icon" variant="ghost">
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="bg-[var(--color-purdue-gold)] text-[var(--color-purdue-black)]">
                                <DialogHeader>
                                  <DialogTitle className="font-semibold">
                                    Delete Folder
                                  </DialogTitle>
                                </DialogHeader>
                                <div className="space-y-4">
                                  <p>
                                    Are you sure you want to delete the folder
                                    <strong> {f.folder_label}</strong>?
                                  </p>
                                  <p className="text-red-600 font-semibold">
                                    This action cannot be undone.
                                  </p>
                                </div>
                                <DialogFooter>
                                  <Button
                                    onClick={() => {
                                      handleDeleteFolder(
                                        c.course_id,
                                        f.folder_id
                                      );
                                      setDeleteFolderId(null); // close after deleting
                                    }}
                                    className="w-full bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold"
                                  >
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    Delete
                                  </Button>
                                </DialogFooter>
                              </DialogContent>
                            </Dialog>

                            <Dialog
                              open={addFileFolderId === f.folder_id}
                              onOpenChange={(open) =>
                                setAddFileFolderId(open ? f.folder_id : null)
                              }
                            >
                              <DialogTrigger asChild>
                                <Button size="icon" variant="ghost">
                                  <Plus className="h-4 w-4 mr-2" />
                                </Button>
                              </DialogTrigger>
                              <DialogContent className="bg-[var(--color-purdue-gold)] text-[var(--color-purdue-black)]">
                                <DialogHeader>
                                  <DialogTitle>
                                    Add File to “{f.folder_label}”
                                  </DialogTitle>
                                </DialogHeader>
                                <Card>
                                  <CardHeader>
                                    <CardTitle>Upload a File</CardTitle>
                                    <CardDescription>
                                      Select a file to upload and click the
                                      submit button.
                                    </CardDescription>
                                  </CardHeader>
                                  <CardContent>
                                    <form
                                      onSubmit={(e) =>
                                        handleUploadSubmit(e, f.folder_id)
                                      }
                                      className="space-y-4"
                                    >
                                      <div className="flex items-center justify-center w-full">
                                        <label
                                          htmlFor="dropzone-file"
                                          className="flex flex-col items-center justify-center w-full h-64 border-2  rounded-lg cursor-pointer bg-[var(--color-purdue-brown)] hover:opacity-90 text-[var(--color-purdue-black)]"
                                        >
                                          <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                            <Upload className="w-10 h-10 text-[var(--color-purdue-black)]" />
                                            <p className="mb-2 text-sm text-[var(--color-purdue-black)]">
                                              <span className="font-semibold">
                                                Click to upload
                                              </span>{" "}
                                              or drag and drop
                                            </p>
                                            <p className="text-xs text-[var(--color-purdue-black)]">
                                              PDF (MAX. 100 MB)
                                            </p>
                                          </div>
                                          <input
                                            id="dropzone-file"
                                            type="file"
                                            className="hidden"
                                            onChange={handleFileChange}
                                          />
                                        </label>
                                      </div>
                                      {selectedFile && (
                                        <div className="flex items-center justify-between">
                                          <div>
                                            <p className="font-medium">
                                              {selectedFile.name}
                                            </p>
                                            <p className="text-sm text-muted-foreground">
                                              {(
                                                selectedFile.size / 100
                                              ).toFixed(2)}{" "}
                                              MB
                                            </p>
                                          </div>
                                          <Button
                                            className="bg-[var(--color-purdue-brown)] hover:opacity-90 text-[var(--color-purdue-black)]"
                                            type="submit"
                                          >
                                            Upload
                                          </Button>
                                        </div>
                                      )}
                                    </form>
                                  </CardContent>
                                </Card>
                                {/*}
                                <form
                                  onSubmit={(e) =>
                                    handleUploadSubmit(e, f.folder_id)
                                  }
                                  className="space-y-4"
                                >
                                  <Input
                                    type="file"
                                    accept="*"
                                    onChange={handleFileChange}
                                    className="block w-full"
                                  />
                                  {selectedFile && (
                                    <div className="flex items-center justify-between">
                                      <div>
                                        <p>{selectedFile.name}</p>
                                        <p className="text-sm">
                                          {(selectedFile.size / 1024).toFixed(
                                            1
                                          )}{" "}
                                          KB
                                        </p>
                                      </div>
                                      <Button type="submit">Upload</Button>
                                    </div>
                                  )}
                                </form>
                                */}
                              </DialogContent>
                            </Dialog>
                          </div>
                        </li>
                      ))
                    ) : (
                      <p className="italic text-gray-500 ml-3 mb-2">
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
