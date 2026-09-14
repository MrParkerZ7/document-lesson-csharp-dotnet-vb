# -*- coding: utf-8 -*-
"""
roster.py — the curriculum: one row per lesson. Lesson modules read their META identity from here, and
lessons that print the learning path (01) or cross-reference another lesson use it, so a rename happens
in one place. Not a lesson module (build_lessons.py only loads lesson_NN.py).

hours    = suggested study time, the author's ESTIMATE
transfer = share of the lesson a Java/Kotlin/TypeScript/Python engineer already knows under another
           name, the author's ESTIMATE (0-100) — it drives the "transfer map" chart in lesson 01
phase    = learning-path phase shown in lesson 01's diagram
"""

ROSTER = [
    # num, slug, title, maps_from_short, hours, transfer, phase
    (1, "dotnet-platform-map", "The .NET Platform Map",
     "JVM · Maven Central · GraalVM native-image", 4, 80, "A · Foundations"),
    (2, "csharp-language-essentials", "C# Language Essentials",
     "Java 21 · Kotlin · TypeScript syntax", 6, 70, "A · Foundations"),
    (3, "types-oop-generics", "Types, OOP & Generics",
     "Java/Kotlin OOP · SOLID · type erasure", 6, 85, "A · Foundations"),
    (4, "linq-collections-functional", "Collections, LINQ & Functional C#",
     "Java Streams · Kotlin collections · TS array methods", 5, 75, "A · Foundations"),
    (5, "async-concurrency", "Async, Tasks & Concurrency",
     "Kotlin coroutines · Spring WebFlux · Node event loop", 7, 55, "B · Runtime & codebase"),
    (6, "vbnet-legacy-estates", "VB.NET for Legacy Estates",
     "Java EE / JSP legacy maintenance · polyglot repos", 5, 35, "B · Runtime & codebase"),
    (7, "solutions-monorepo-build", "Solutions, MSBuild & Mono-repos",
     "Gradle Kotlin DSL · Maven multi-module · Lerna", 5, 70, "B · Runtime & codebase"),
    (8, "aspnet-core-web-apis", "ASP.NET Core Web APIs",
     "Spring Boot · NestJS · Express", 7, 75, "C · Services"),
    (9, "data-access-efcore", "Data Access with EF Core",
     "JPA/Hibernate · TypeORM · Flyway/Liquibase", 6, 70, "C · Services"),
    (10, "testing-tdd-coverage", "Testing, TDD & 100% Coverage",
     "JUnit · Mockito · MockMvc · Postman · BDD", 6, 85, "C · Services"),
    (11, "security-identity", "Security & Identity with Entra ID",
     "Spring Security · OAuth2/OIDC · Entra ID / AD B2C", 6, 85, "D · Production"),
    (12, "cloud-native-modernization", "Cloud-Native .NET on AWS & Modernization",
     "AWS Lambda · ECS Fargate · Terraform · GitHub Actions · IIS estates", 8, 80, "D · Production"),
]


def row(num):
    for r in ROSTER:
        if r[0] == num:
            return r
    raise KeyError(num)


def meta(num, subtitle, objectives, maps_from):
    """Build a lesson's META from its roster row plus the lesson-specific text."""
    n, slug, title, short, _hours, _transfer, _phase = row(num)
    return {"num": n, "slug": slug, "title": title, "subtitle": subtitle,
            "objectives": objectives, "maps_from": maps_from, "maps_from_short": short}


def ref(num):
    """How one lesson names another in prose: 'lesson 05 (Async, Tasks & Concurrency)'."""
    n, _slug, title, *_ = row(num)
    return f"lesson {n:02d} ({title})"
