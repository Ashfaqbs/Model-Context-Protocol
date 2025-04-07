### What are MCP Servers?

MCP stands for **Model Control Protocol**. It’s a protocol designed to facilitate the interaction between AI models and external data services, enabling AI models to interact with custom data sources and perform specific tasks in a standardized manner.

An **MCP server** is a server that implements the Model Control Protocol, exposing data and functionality through a set of defined tools that can be accessed by AI models. These tools allow the AI models to query the server, retrieve data, or perform actions based on the exposed functionality.

### Why Use MCP Servers?

1. **Standardized Communication**: MCP servers standardize how AI models interact with data and services. This makes it easier to integrate different data sources or services with AI models without needing custom integration for each one.

2. **Simplifies AI-Data Interaction**: AI models can communicate with an MCP server to access structured data or perform tasks like searching, retrieving, or manipulating data. For example, if we have a server with course data, an AI model can request a list of courses or search for a specific course by title.

3. **Separation of Concerns**: By exposing data via tools on the MCP server, we separate the concerns of managing data and the logic of interacting with AI models. The AI doesn't need to know about the internal workings of our data source; it just uses the exposed tools.

4. **Flexibility**: MCP servers allow we to build custom, domain-specific tools for AI models to use. For example, a course database can be turned into an MCP server, with tools for searching, listing, or even updating course details. The AI can access these tools easily, making the data dynamic and accessible.

### How Does an MCP Server Work?

1. **Define Tools**: On the MCP server, we define tools (functions or services) that the AI model can invoke. These tools typically include descriptions and can be registered with the server to be exposed to external systems (like AI models).

2. **Tool Invocation**: When an AI model needs to interact with the data, it sends requests to the MCP server using these defined tools. For example, an AI model could request a list of all courses or search for a course by name.

3. **Data Interaction**: The server performs the requested operation and sends the results back to the AI model. This interaction happens over a communication channel defined by the protocol (often STDIO, but it can also be over a network in some cases).

### Why Use MCP Servers for AI Models?

1. **Simplifies Integration**: we don’t have to write complex integration code each time we want to expose data or services to an AI model. The standardized MCP tools handle the heavy lifting.

2. **Easily Extendable**: As our requirements grow, we can extend the MCP server by adding new tools, exposing new functionalities, or hooking it up to new data sources. This makes it very easy to evolve our AI system.

3. **Real-Time Data Access**: By using an MCP server, AI models can get up-to-date, real-time access to external data sources (e.g., course data, weather data, financial data) without needing to directly interact with the databases or services.

### Example

Imagine we have an AI model that helps students find online courses. The AI model can send requests to an MCP server exposed by a course data provider (like a website or a database of online courses). It could invoke tools like:
- `get_all_courses` to get a list of available courses.
- `search_courses_by_title` to find a course by name.

The AI model doesn’t need to worry about how the data is stored or retrieved—it just interacts with the tools exposed by the MCP server.

### In Summary:

- **MCP servers** are a way to expose data and functionality in a standardized manner, so AI models can easily interact with them.
- They enable **seamless integration** between AI models and various data sources.
- They provide **flexibility** and **scalability** to build domain-specific tools and services for AI models.



# Spring AI MCP Server for Course Information

## Overview

This repo contains a Spring Boot application that sets up an MCP (Model Control Protocol) server for sharing course information to LLMS. It’s a simple setup where we can expose our course data using the Spring AI MCP framework, allowing AI models to interact with our data in a standardized MCP way.

The server offers two main tools:
- One tool to get a list of all available courses.
- Another tool to search for courses by title.

This setup is a good starting point for creating our own MCP server or for hooking up external data sources to AI models using Spring AI.

## Project Requirements

- **Java 24**
- **Maven 3.8+**
- **Spring Boot 3.4.4**
- **Spring AI 1.0.0-M6**

## Dependencies

The project uses a couple of important dependencies:

- **Spring AI MCP Server**: This provides the core components for creating an MCP-compatible server.
  ```xml
  <dependency>
      <groupId>org.springframework.ai</groupId>
      <artifactId>spring-ai-mcp-server-spring-boot-starter</artifactId>
  </dependency>
  ```

## Getting Started

### Prerequisites

- Java 24 installed on our system.
- Maven set up for managing dependencies.

### Setting Up the Project

1. Check out the project structure to understand what’s inside:
    - `Course.java`: A simple record to represent course data.
    - `CourseService.java`: The service that uses MCP tool annotations.
    - `CoursesApplication.java`: The main class that registers the tools.
    - `application.properties`: This file contains the MCP server’s settings.

2. The application is configured as a non-web app, using STDIO transport for MCP communication. Here's the configuration in `application.properties`:
   ```properties
   spring.main.web-application-type=none
   spring.ai.mcp.server.name=course-mcp
   spring.ai.mcp.server.version=0.0.1

   # These settings make sure STDIO transport works
   spring.main.banner-mode=off
   logging.pattern.console=
   ```

## How to Run the Application

```bash
mvn spring-boot:run
```

This starts up the MCP server, but it doesn't open any web ports or anything like that. It's all handled through standard input/output (STDIO).

Once the app is running, the server registers two tools with the MCP:
- `course_get_courses`: Fetches a list of available courses.
- `course_get_course`: Retrieves a specific course by title.

And we need to register or connect the MCP spring boot server to the MCP Client in our case the Claude Desktop.
- We can register this via creating a file claude_desktop_config.json and adding a new MCP server in the Claude Desktop. sample path: "C:\Users\ashfaq\AppData\Roaming\Claude\claude_desktop_config.json"

## Understanding the Code

### Defining Data Models

We’re using a simple record to represent course data:

```java
public record Course(String title, String url) {
}
```

### Implementing Tool Functions

In `CourseService.java`, we’ve created methods that are exposed as tools using the `@Tool` annotation:

```java

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

```

### Registering Tools with MCP

In the main app class (`CoursesApplication.java`), tools are registered with the MCP framework:

```java
@SpringBootApplication
public class CoursesApplication {

    public static void main(String[] args) {
        SpringApplication.run(CoursesApplication.class, args);
    }

    @Bean
    public List<ToolCallback> courseTools(CourseService courseService) {
        return List.of(ToolCallbacks.from(courseService));
    }
}
```

The `ToolCallbacks.from()` method scans the service class for `@Tool` annotations and registers them with MCP.

## Configuration for Course MCP Server

To use this MCP server with the Claude Desktop client, here’s how we can configure it:

```json


{
  
  "mcpServers": {
    "course-mcp": {
      "command": "C:\\Program Files\\Java\\jdk-24\\bin\\java",
      "args": [
        "-jar",
        "C:\\tmp\\courses-mcp-example\\course.jar"
      ]
  
    }
  }
  
//  other mcp servers link : https://modelcontextprotocol.io/examples
}
```

This config:
- Sets up the MCP server with the name `course-mcp`.
- Points to the correct Java executable and JAR file path for the application.
- Restart the Claude desktop app and when asked about the question related to the course it will automatically fetch the answer from the MCP server.


## Extending the Project

we can build on this project by:
1. **Adding more courses**: Just modify the `init()` method in `CourseService` to add more courses.
2. **Creating new tools**: Add more methods annotated with `@Tool` to expose additional functionality.
3. **Implementing a database**: If we want persistent storage, swap out the in-memory list with a database.
4. **Adding search**: Make the search feature more advanced by allowing partial matching or filtering by other criteria.

Here’s an example of adding a search feature:

```java
@Tool(name = "course_search_courses", description = "Search courses by keyword")
public List<Course> searchCourses(String keyword) {
    return courses.stream()
            .filter(course -> course.title().toLowerCase().contains(keyword.toLowerCase()))
            .collect(Collectors.toList());
}
```

## Conclusion

This Spring AI MCP Server is a great starting point for exposing course data through the Model Control Protocol. It provides a clean, extensible framework that can be customized and expanded. we can build more powerful data providers and integrate AI models with our course data.

If we're looking to explore Spring AI or the Model Control Protocol further,check out the official documentation for more details.

ref:
https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html
https://modelcontextprotocol.io/introduction
https://github.com/danvega/dv-courses-mcp

---