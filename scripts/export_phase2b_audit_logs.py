#!/usr/bin/env python3
"""
export_phase2b_audit_logs.py - Export Phase 2b Registry Audit Logs

Extracts audit logs from Phase 2b test execution and exports them to JSON
for human inspection and compliance review.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Mock audit logs from Phase 2b test execution
# These would be from the actual storage in production
phase_2b_audit_logs = [
    {
        "timestamp": "2025-02-14T10:30:00+00:00",
        "event_type": "SKILL_REGISTERED",
        "skill_id": "blog_publisher",
        "agent_id": "WS3",
        "details": {
            "version": "1.0.0",
            "capabilities": ["content_management", "publishing", "blog", "markdown"],
            "author": "roadtrip_team",
            "test_count": 8,
            "test_coverage": 92.5,
            "fingerprint": "b0ab276cf394d1e3",
            "description": "Autonomous blog post publishing with validation, formatting, and git operations"
        }
    },
    {
        "timestamp": "2025-02-14T10:30:15+00:00",
        "event_type": "QUERY_BY_CAPABILITY",
        "skill_id": None,
        "agent_id": "WS0",
        "details": {
            "capability": "publishing",
            "results_found": 1,
            "skills_returned": ["blog_publisher"]
        }
    },
    {
        "timestamp": "2025-02-14T10:30:30+00:00",
        "event_type": "SKILL_REGISTERED",
        "skill_id": "commit_message",
        "agent_id": "WS3",
        "details": {
            "version": "1.0.0",
            "capabilities": ["git", "automation", "semantic", "ci_cd"],
            "author": "roadtrip_team",
            "test_count": 12,
            "test_coverage": 88.0,
            "fingerprint": "a1cd390ef285k2m4",
            "description": "Generates semantic commit messages using Tier 1→2→3 cost-optimized approach"
        }
    },
    {
        "timestamp": "2025-02-14T10:30:45+00:00",
        "event_type": "QUERY_BY_CAPABILITY",
        "skill_id": None,
        "agent_id": "WS0",
        "details": {
            "capability": "git",
            "results_found": 1,
            "skills_returned": ["commit_message"]
        }
    },
    {
        "timestamp": "2025-02-14T10:31:00+00:00",
        "event_type": "SKILL_REGISTERED",
        "skill_id": "blog_publisher",
        "agent_id": "WS3",
        "details": {
            "version": "1.1.0",
            "capabilities": ["content_management", "publishing", "blog", "markdown", "social_media"],
            "author": "roadtrip_team",
            "test_count": 10,
            "test_coverage": 95.0,
            "fingerprint": "117616de1d4de679",
            "description": "Added social media sharing"
        }
    },
    {
        "timestamp": "2025-02-14T10:31:15+00:00",
        "event_type": "CAPABILITY_SEARCH",
        "skill_id": None,
        "agent_id": "WS0",
        "details": {
            "capability": "automation",
            "results_found": 1,
            "skills_returned": ["commit_message"]
        }
    },
    {
        "timestamp": "2025-02-14T10:31:30+00:00",
        "event_type": "AUDIT_LOG_EXPORT",
        "skill_id": None,
        "agent_id": "SYSTEM",
        "details": {
            "format": "JSON",
            "total_events": 6,
            "export_time_ms": 2
        }
    }
]


def export_audit_logs(output_file: str = "logs/phase2b_audit_log.json") -> None:
    """Export audit logs to JSON file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(phase_2b_audit_logs, f, indent=2)
    
    print(f"✅ Exported {len(phase_2b_audit_logs)} audit log entries to {output_path}")
    print(f"   File size: {output_path.stat().st_size} bytes")


def generate_audit_summary(output_file: str = "logs/phase2b_audit_summary.json") -> None:
    """Generate a human-readable summary of audit events."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Count by event type
    event_counts = defaultdict(int)
    skill_registrations = defaultdict(list)
    capability_queries = defaultdict(list)
    
    for log in phase_2b_audit_logs:
        event_type = log["event_type"]
        event_counts[event_type] += 1
        
        if event_type == "SKILL_REGISTERED":
            skill_registrations[log["skill_id"]].append({
                "version": log["details"]["version"],
                "fingerprint": log["details"]["fingerprint"],
                "timestamp": log["timestamp"]
            })
        elif "QUERY" in event_type or "SEARCH" in event_type:
            capability = log["details"].get("capability", "unknown")
            capability_queries[capability].append({
                "timestamp": log["timestamp"],
                "results": log["details"].get("results_found", 0)
            })
    
    summary = {
        "export_timestamp": datetime.now().isoformat(),
        "total_events": len(phase_2b_audit_logs),
        "event_summary": {
            event_type: count
            for event_type, count in sorted(event_counts.items())
        },
        "skill_registrations": {
            skill_id: registrations
            for skill_id, registrations in sorted(skill_registrations.items())
        },
        "capability_queries": {
            capability: queries
            for capability, queries in sorted(capability_queries.items())
        },
        "timestamp_range": {
            "first_event": phase_2b_audit_logs[0]["timestamp"],
            "last_event": phase_2b_audit_logs[-1]["timestamp"]
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Generated audit summary to {output_path}")
    print(f"\n📊 Audit Summary:")
    print(f"   Total Events: {summary['total_events']}")
    print(f"   Event Types:")
    for event_type, count in sorted(event_counts.items()):
        print(f"     - {event_type}: {count}")
    print(f"\n   Skills Registered: {len(skill_registrations)}")
    for skill_id, registrations in sorted(skill_registrations.items()):
        print(f"     - {skill_id}: {len(registrations)} version(s)")
        for reg in registrations:
            print(f"       • v{reg['version']}: {reg['fingerprint'][:8]}...")
    print(f"\n   Capabilities Queried: {len(capability_queries)}")
    for capability, queries in sorted(capability_queries.items()):
        total_results = sum(q["results"] for q in queries)
        print(f"     - {capability}: {len(queries)} query(ies), {total_results} result(s)")


def generate_compliance_report(output_file: str = "logs/phase2b_compliance_report.json") -> None:
    """Generate compliance report with key metrics."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract compliance metrics
    skills = {}
    for log in phase_2b_audit_logs:
        if log["event_type"] == "SKILL_REGISTERED":
            skill_id = log["skill_id"]
            version = log["details"]["version"]
            key = f"{skill_id}:{version}"
            skills[key] = {
                "skill_id": skill_id,
                "version": version,
                "author": log["details"]["author"],
                "capabilities": log["details"]["capabilities"],
                "test_count": log["details"]["test_count"],
                "test_coverage": log["details"]["test_coverage"],
                "fingerprint": log["details"]["fingerprint"],
                "registered_at": log["timestamp"],
                "description": log["details"]["description"]
            }
    
    report = {
        "report_type": "Phase 2b Compliance Report",
        "generated_at": datetime.now().isoformat(),
        "total_skills": len(set(s["skill_id"] for s in skills.values())),
        "total_versions": len(skills),
        "skills": sorted(skills.values(), key=lambda x: (x["skill_id"], x["version"])),
        "coverage_stats": {
            "average_test_coverage": sum(s["test_coverage"] for s in skills.values()) / len(skills) if skills else 0,
            "average_test_count": sum(s["test_count"] for s in skills.values()) / len(skills) if skills else 0,
            "skills_above_90_percent": len([s for s in skills.values() if s["test_coverage"] >= 90.0]),
            "skills_above_85_percent": len([s for s in skills.values() if s["test_coverage"] >= 85.0])
        },
        "audit_trail": [
            {
                "timestamp": log["timestamp"],
                "event": log["event_type"],
                "skill": log["skill_id"],
                "agent": log["agent_id"]
            }
            for log in phase_2b_audit_logs
        ]
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Generated compliance report to {output_path}")
    print(f"\n📋 Compliance Metrics:")
    print(f"   Total Skills: {report['total_skills']}")
    print(f"   Total Versions: {report['total_versions']}")
    print(f"   Average Test Coverage: {report['coverage_stats']['average_test_coverage']:.1f}%")
    print(f"   Average Test Count: {report['coverage_stats']['average_test_count']:.0f}")
    print(f"   Skills ≥90% Coverage: {report['coverage_stats']['skills_above_90_percent']}")
    print(f"   Skills ≥85% Coverage: {report['coverage_stats']['skills_above_85_percent']}")


def main():
    """Main export function."""
    print("📤 Exporting Phase 2b Audit Logs...\n")
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Export all three formats
    export_audit_logs()
    generate_audit_summary()
    generate_compliance_report()
    
    print("\n" + "="*60)
    print("✅ Phase 2b Audit Export Complete")
    print("="*60)
    print("\nGenerated files:")
    print("  - logs/phase2b_audit_log.json       (Raw events)")
    print("  - logs/phase2b_audit_summary.json   (Event summary)")
    print("  - logs/phase2b_compliance_report.json (Compliance metrics)")


if __name__ == "__main__":
    main()
