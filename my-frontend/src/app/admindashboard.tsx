"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { getJson, postJson } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";

interface Course {
  id: number;
  course_code: string;
  course_title: string;
}

export default function AdminDashboard() {
  const { userId, admin, loading } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [code, setCode] = useState("");
  const [title, setTitle] = useState("");
  const router = useRouter();

  // 1) Guard
  if (loading) return null;
  if (!userId || !admin) {
    router.replace("/login");
    return null;
  }

  // 2) Extract loader so we can call it anywhere
  const loadCourses = useCallback(async () => {
    try {
      const data = await getJson<Course[]>("/courses", true);
      setCourses(data);
    } catch (err) {
      console.error("Failed to load courses", err);
    }
  }, []);

  // 3) Load on mount
  useEffect(() => {
    loadCourses();
  }, [loadCourses]);

  // 4) Create + join + reload
  const handleCreate = async () => {
    if (!code.trim() || !title.trim()) return;

    try {
      // create course → returns new ID
      const newId = await postJson<number>(
        "/courses/create",
        { course_code: code, course_title: title },
        true
      );

      // join course as admin/owner
      await postJson<boolean>("/users/joincourse", { course_code: code }, true);

      // clear inputs
      setCode("");
      setTitle("");

      // reload the list
      await loadCourses();
    } catch (err) {
      console.error("Error creating/joining course", err);
    }
  };

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold text-[var(--color-purdue-gold)] mb-6">
        Admin Dashboard
      </h1>

      <section className="mb-10">
        <h2 className="text-2xl font-semibold text-[var(--color-purdue-gold)] mb-4">
          Your Courses
        </h2>

        {courses.length > 0 ? (
          <ul className="space-y-2">
            {courses.map((c) => (
              <li key={c.id}>
                <Link
                  href={`/courses/${c.id}`}
                  className="text-lg text-blue-600 hover:underline"
                >
                  {c.course_title} ({c.course_code})
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="italic text-gray-500">No courses created yet.</p>
        )}
      </section>

      <section>
        <h3 className="text-xl font-semibold mb-2">Create New Course</h3>
        <div className="flex flex-col max-w-sm space-y-2">
          <Input
            placeholder="Course Code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
          <Input
            placeholder="Course Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <Button
            onClick={handleCreate}
            className="bg-[var(--color-purdue-gold)] hover:bg-[var(--color-purdue-brown)] text-[var(--color-purdue-black)]"
          >
            Create & Join
          </Button>
        </div>
      </section>
    </div>
  );
}
