package com.mcp.courses;

import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class CourseService {

    private static final Logger log = LoggerFactory.getLogger(CourseService.class);
    private List<Course> courses = new ArrayList<>();

    @Tool(name = "find_courses", description = "Get a list of courses from authorx")
    public List<Course> getCourses() {
        return courses;
    }

    @Tool(name = "find_course_title", description = "Get a single courses from authorx by title")
    public Course getCourse(String title) {
        return courses.stream().filter(course -> course.title().equals(title)).findFirst().orElse(null);
    }

    @PostConstruct
    public void init() {
        courses.addAll(List.of(
                new Course("System Design Primer", "https://www.youtube.com/watch?v=SqcXvc3ZmRU&list=PLMCXHnjXnTnvo6alSjVkgxV-VH6EPyvoX"),
                new Course("Spring Boot Tutorial for Beginners - 2023 Crash Course using Spring Boot 3","https://youtu.be/UgX5lgv4uVM")
        ));
    }

}
