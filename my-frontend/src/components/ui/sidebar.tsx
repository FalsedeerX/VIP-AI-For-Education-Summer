import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import { getJson, postJson, deleteJson } from "@/lib/api";
import { useEffect, useCallback, Fragment } from "react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import {
  Plus,
  FolderPlus,
  PanelLeftClose,
  PanelLeftOpen,
  Trash2,
  BookA,
  Folder,
  MessageSquare,
} from "lucide-react";
import { Separator } from "@/components/ui/separator";

interface Course {
  course_id: number;
  title: string;
}

interface Folder {
  folder_label: string;
  folder_id: number;
}

interface Chat {
  chat_id: string;
  title: string;
}

export default function Sidebar({
  isDrawerOpen,
  setIsDrawerOpen,
}: {
  isDrawerOpen: boolean;
  setIsDrawerOpen: (open: boolean) => void;
}) {
  const router = useRouter();
  const { userId, loading } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [foldersByCourse, setFoldersByCourse] = useState<{
    [key: number]: Folder[];
  }>({});
  const [chatsByFolder, setChatsByFolder] = useState<Record<number, Chat[]>>(
    {}
  );
  const [selectedCourse, setSelectedCourse] = useState<number | null>(null);
  const [selectedFolder, setSelectedFolder] = useState<number | null>(null);
  const [selectedChat, setSelectedChat] = useState<string | null>(null);
  const [showAddCourse, setShowAddCourse] = useState(false);
  const [newCourseCode, setNewCourseCode] = useState("");
  const [showAddChat, setShowAddChat] = useState(false);
  const [newChatName, setNewChatName] = useState("");

  // Redirect if not authenticated
  /*
  if (loading) return null;
  if (!userId) {
    router.replace("/login");
    return null;
  }
  */

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

  // Fetch chats for a folder
  const loadChats = async (folderId: number) => {
    try {
      // Assuming your GET /folders POST returns e.g. Chat[]
      const data = await postJson<Chat[]>(
        "/folders",
        { folder_id: folderId },
        true
      );
      setChatsByFolder((prev) => ({
        ...prev,
        [folderId]: data,
      }));
    } catch (err) {
      console.error(`Failed to load chats for folder ${folderId}`, err);
    }
  };

  // load course upon render
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
    loadChats(folderId);
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

  const handleNewChat = async () => {
    if (!newChatName.trim()) return;
    try {
      const id = await postJson<string>(
        "/chats/create",
        { title: newChatName },
        true
      );
      await postJson<boolean>(
        "/chats/organize",
        { folder_id: selectedFolder, chat_id: id },
        true
      );

      setNewChatName("");
      setShowAddChat(false);
      loadChats(selectedFolder!);
    } catch (err) {
      console.error("Error creating chat", err);
    }
  };

  const handleDeleteChat = async (chatId: string) => {
    if (!confirm("Really delete this chat?")) return;
    try {
      await deleteJson<boolean>(`/chats/delete/${chatId}`, {}, true);
      loadChats(selectedFolder!);
    } catch (err) {
      console.error(`Failed to delete chat ${chatId}`, err);
    }
  };

  // login guard
  if (loading) return null;
  if (!userId) {
    router.replace("/login");
    return null;
  }
  return (
    <aside
      className={`
        flex-shrink-0
        h-full
        bg-[var(--color-purdue-brown)]
        transition-all duration-200
        ${isDrawerOpen ? "w-80" : "w-16"}
      `}
    >
      {/* trigger and content all in here, no `fixed` */}
      <div className="flex items-center justify-between p-4">
        <button onClick={() => setIsDrawerOpen(!isDrawerOpen)}>
          {isDrawerOpen ? <PanelLeftClose /> : <PanelLeftOpen />}
        </button>
      </div>
      {isDrawerOpen && (
        <nav className="p-4 overflow-y-auto space-y-4">
          {/* Drawer */}

          <div className="flex items-center justify-between pb-4 bg-[var(--color-purdue-brown)]">
            <h5
              id="drawer-navigation-label"
              className="text-[var(--color-purdue-black)] uppercase text-xl font-bold tracking-wider"
            >
              Menu
            </h5>
          </div>

          <div>
            <Dialog open={showAddCourse} onOpenChange={setShowAddCourse}>
              <DialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full flex items-center justify-center bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold text-md"
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
          </div>

          <Separator
            className="my-4 text-[var(--color-purdue-black)]"
            style={{ height: "4px" }}
          />
          {/* Course List Header */}
          <div className="flex items-center justify-between ">
            <h2 className="text-[var(--color-purdue-black)] uppercase text-lg font-bold tracking-wider">
              Courses
            </h2>
          </div>

          {/* Course List */}
          <div className="py-4 overflow-y-auto">
            <ul className="space-y-2 font-medium">
              {courses.map((course) => (
                <Fragment key={course.course_id}>
                  <Button
                    onClick={() => handleSelectCourse(course.course_id)}
                    className={
                      "w-full flex items-center p-2 rounded-lg bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold text-md" +
                      (selectedCourse === course.course_id ? "" : "")
                    }
                  >
                    <BookA className="mr-2 h-4 w-4" />
                    {course.title}
                  </Button>

                  {selectedCourse === course.course_id && (
                    <ul className="pl-4 space-y-2">
                      {/* <Separator
                      className="my-2 text-[var(--color-purdue-black)]"
                      style={{ height: "2px" }}
                    />
                    */}
                      {/* Folders for selected course */}
                      {(foldersByCourse[course.course_id] || []).map(
                        (folder) => (
                          <li key={folder.folder_id}>
                            <Button
                              onClick={() =>
                                handleSelectFolder(folder.folder_id)
                              }
                              className={
                                "w-full flex items-center p-2 rounded-lg bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold text-md" +
                                (selectedFolder === folder.folder_id ? "" : "")
                              }
                            >
                              <Folder className="mr-2 h-4 w-4" />
                              {folder.folder_label}
                            </Button>
                            {/* Chats for selected folder */}
                            {selectedCourse === course.course_id &&
                              selectedFolder == folder.folder_id && (
                                <ul className="pl-4 space-y-2 pt-2">
                                  {/* <Separator
                                className="my-2 text-[var(--color-purdue-black)]"
                                style={{ height: "2px" }}
                              /> */}
                                  {(chatsByFolder[folder.folder_id] || []).map(
                                    (chat) => (
                                      <li key={chat.chat_id}>
                                        <Button
                                          onClick={() =>
                                            router.push(`/chat/${chat.chat_id}`)
                                          }
                                          className="relative w-full p-2 flex items-center rounded-lg bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold text-md"
                                        >
                                          {/* 1) Centered icon + title */}
                                          <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 flex items-center pointer-events-none">
                                            <MessageSquare className="mr-2 h-4 w-4" />
                                            <span>{chat.title}</span>
                                          </div>

                                          {/* 2) Trash icon at far right */}
                                          <Button
                                            asChild
                                            size="icon"
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              handleDeleteChat(chat.chat_id);
                                            }}
                                            className=" ml-auto bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] "
                                          >
                                            <Trash2
                                              className="h-4 w-4"
                                              strokeWidth={2.5}
                                            />
                                          </Button>
                                        </Button>
                                      </li>
                                    )
                                  )}
                                  <li>
                                    <div>
                                      <Dialog
                                        open={showAddChat}
                                        onOpenChange={setShowAddChat}
                                      >
                                        <DialogTrigger asChild>
                                          <Button
                                            onClick={() => setShowAddChat(true)}
                                            className="w-full flex items-center p-2 rounded-lg bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold text-md"
                                          >
                                            <Plus className="mr-2 h-4 w-4" />
                                            New Chat
                                          </Button>
                                        </DialogTrigger>

                                        <DialogContent className="bg-[var(--color-purdue-gold)] text-[var(--color-purdue-black)]">
                                          <DialogHeader>
                                            <DialogTitle>
                                              Start a New Chat
                                            </DialogTitle>
                                          </DialogHeader>

                                          <div className="space-y-4">
                                            <Input
                                              placeholder="Chat Name"
                                              value={newChatName}
                                              onChange={(e) =>
                                                setNewChatName(e.target.value)
                                              }
                                            />
                                          </div>

                                          <DialogFooter>
                                            <Button
                                              onClick={async () => {
                                                await handleNewChat();
                                                setShowAddChat(false); // close dialog after creation
                                                setNewChatName(""); // clear input for next time
                                              }}
                                              className="w-full bg-[var(--color-purdue-black)] hover:opacity-90 text-[var(--color-purdue-gold)] font-semibold"
                                            >
                                              <FolderPlus className="mr-2 h-4 w-4" />
                                              Create
                                            </Button>
                                          </DialogFooter>
                                        </DialogContent>
                                      </Dialog>
                                    </div>
                                  </li>
                                </ul>
                              )}
                          </li>
                        )
                      )}
                    </ul>
                  )}
                </Fragment>
              ))}
            </ul>
          </div>
        </nav>
      )}
    </aside>
  );
}
