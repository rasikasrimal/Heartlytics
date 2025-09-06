# Project Gantt Chart

The following Gantt chart outlines the major phases, tasks, and milestones for the HeartLytics web application. The chart renders in both GitHub and local Markdown preview.

```mermaid
gantt
    dateFormat  YYYY-MM-DD
    title HeartLytics Development Timeline
    excludes weekends

    section Planning
    Requirements Gathering          :done,    req, 2024-01-01,2024-01-14
    Feasibility Study               :done,    feas, 2024-01-15,2024-01-28

    section Development
    Backend Implementation          :active,  back, 2024-02-01,2024-03-15
    Frontend Integration            :         front, after back, 30d
    Machine Learning Model          :         ml,   2024-02-15,2024-03-15

    section Testing
    Unit & Integration Tests        :         test, 2024-03-16,2024-03-31
    User Acceptance Testing         :         uat,  2024-04-01,2024-04-15

    section Deployment
    Production Deployment           :milestone, deploy, 2024-04-20, 0d

    section Post-Deployment
    Monitoring and Maintenance      :         post, 2024-04-21,2024-05-31
```

## Summary
- **Planning** ensures clear requirements and feasibility.
- **Development** covers backend, frontend, and model building.
- **Testing** verifies functionality and user satisfaction.
- **Deployment** marks the production release.
- **Post-Deployment** includes monitoring and ongoing maintenance.

