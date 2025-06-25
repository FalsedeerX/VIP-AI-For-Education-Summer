import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { getJson } from "@/lib/api";

interface Course {
  id: string;
  title: string;
  folders?: Folder[];
}

interface Folder {
  id: string;
  title: string;
  chats?: Chat[];
}

interface Chat {
  id: string;
  title: string;
  messages?: any[];
}

export default function MainScreen() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<
    Record<string, boolean>
  >({});
  const [newChatTitle, setNewChatTitle] = useState("");
  const [creatingChatFolderId, setCreatingChatFolderId] = useState<
    string | null
  >(null);
  const [activeChat, setActiveChat] = useState<Chat | null>(null);

  // Placeholder fetch - replace with real endpoint calls
  useEffect(() => {
    async function loadCourses() {
      const data: Course[] = await await getJson<{}>("/users/getcourses", true);
      setCourses(data);
    }
    loadCourses();
  }, []);

  const toggleFolder = (folderId: string) => {
    setExpandedFolders((prev) => ({
      ...prev,
      [folderId]: !prev[folderId],
    }));
  };

  const startNewChat = (folderId: string) => {
    setCreatingChatFolderId(folderId);
  };

  const sendMessage = async () => {
    if (!creatingChatFolderId || !newChatTitle) return;
    // await createChat(creatingChatFolderId, newChatTitle, firstMessage);
    const newChat: Chat = { id: Date.now().toString(), title: newChatTitle };
    // Add to state
    setCourses((cs) =>
      cs.map((c) => {
        if (c.id !== selectedCourse?.id) return c;
        return {
          ...c,
          folders: c.folders?.map((f) =>
            f.id === creatingChatFolderId
              ? {
                  ...f,
                  chats: [...(f.chats || []), newChat],
                }
              : f
          ),
        };
      })
    );
    setActiveChat(newChat);
    setCreatingChatFolderId(null);
    setNewChatTitle("");
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-80 border-r p-4 flex flex-col">
        <Button
          className="mb-4"
          onClick={() => {
            /* open admin course modal */
          }}
        >
          New Course
        </Button>
        <Separator className="mb-4" />
        <div className="overflow-y-auto flex-1">
          {courses.map((course) => (
            <Card key={course.id} className="mb-2">
              <CardContent>
                <h3
                  className="font-semibold cursor-pointer"
                  onClick={() => setSelectedCourse(course)}
                >
                  {course.title}
                </h3>
                {selectedCourse?.id === course.id &&
                  course.folders?.map((folder) => (
                    <div key={folder.id} className="ml-4">
                      <div className="flex justify-between items-center">
                        <span
                          className="cursor-pointer"
                          onClick={() => toggleFolder(folder.id)}
                        >
                          {folder.title}
                        </span>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => startNewChat(folder.id)}
                        >
                          New Chat
                        </Button>
                      </div>
                      {expandedFolders[folder.id] && (
                        <ul className="mt-1 ml-4">
                          {folder.chats?.map((chat) => (
                            <li
                              key={chat.id}
                              className="cursor-pointer"
                              onClick={() => setActiveChat(chat)}
                            >
                              {chat.title}
                            </li>
                          ))}
                          {creatingChatFolderId === folder.id && (
                            <div className="mt-2">
                              <Input
                                placeholder="Chat title..."
                                value={newChatTitle}
                                onChange={(e) =>
                                  setNewChatTitle(e.target.value)
                                }
                                onKeyDown={(e) => {
                                  if (e.key === "Enter") sendMessage();
                                }}
                              />
                              <Button className="mt-1" onClick={sendMessage}>
                                Send First Message
                              </Button>
                            </div>
                          )}
                        </ul>
                      )}
                    </div>
                  ))}
              </CardContent>
            </Card>
          ))}
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 p-6 flex flex-col">
        {activeChat ? (
          <div className="flex-1 border rounded p-4 overflow-y-auto">
            {/* Chat messages go here */}
            <h2 className="text-xl font-semibold mb-4">{activeChat.title}</h2>
            {/* TODO: render messages */}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-gray-500">Select or start a chat to begin</p>
          </div>
        )}
      </main>
    </div>
  );
}
