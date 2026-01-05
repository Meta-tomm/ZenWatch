# Power BI Content Performance Analytics Dashboard

**Date**: 2026-01-03
**Status**: Design Complete
**Purpose**: Build comprehensive Power BI dashboard for analyzing tech content performance, learning Power BI skills for career development

## Overview

A multi-page Power BI dashboard that analyzes content performance across ZenWatch's tech news aggregation platform. Designed to teach intermediate Power BI skills while providing actionable insights about source quality, content characteristics, and system health.

**Learning Goals:**
- Master DAX measures (basic to advanced)
- Build enterprise-standard multi-page dashboards
- Understand data modeling and SQL views
- Learn Power BI Embedded integration
- Create portfolio-ready analytics project

**Business Goals:**
- Identify best-performing content sources
- Understand what content characteristics drive engagement
- Monitor system health and data quality
- Spot trending topics and categories
- Optimize content curation strategy

## Architecture

### Data Model

**SQL Views (Backend)**

Instead of connecting directly to raw tables, create optimized views in PostgreSQL. This follows enterprise best practices and improves performance.

**Core Views:**

1. **vw_article_performance** - Main fact table
```sql
CREATE OR REPLACE VIEW vw_article_performance AS
SELECT
    a.id,
    a.title,
    a.url,
    a.score,
    a.published_at,
    a.created_at,
    a.upvotes,
    a.comments_count,
    a.read_time_minutes,
    a.category,
    a.tags,
    a.is_read,
    a.is_favorite,
    s.name as source_name,
    s.type as source_type,
    -- Calculated columns
    COALESCE(a.upvotes, 0) + COALESCE(a.comments_count, 0) as total_engagement,
    EXTRACT(HOUR FROM a.published_at) as publish_hour,
    EXTRACT(DOW FROM a.published_at) as publish_day_of_week,
    LENGTH(a.title) as title_length,
    CARDINALITY(a.tags) as tag_count,
    DATE(a.published_at) as publish_date,
    CURRENT_DATE - DATE(a.published_at) as days_since_published
FROM articles a
LEFT JOIN sources s ON a.source_id = s.id
WHERE a.is_archived = false;
```

2. **vw_daily_metrics** - Pre-aggregated time series
```sql
CREATE OR REPLACE VIEW vw_daily_metrics AS
SELECT
    DATE(a.published_at) as metric_date,
    s.type as source_type,
    a.category,
    COUNT(*) as article_count,
    AVG(a.score) as avg_score,
    SUM(COALESCE(a.upvotes, 0)) as total_upvotes,
    SUM(COALESCE(a.comments_count, 0)) as total_comments
FROM articles a
LEFT JOIN sources s ON a.source_id = s.id
WHERE a.is_archived = false
GROUP BY DATE(a.published_at), s.type, a.category;
```

3. **vw_source_stats** - Source aggregates
```sql
CREATE OR REPLACE VIEW vw_source_stats AS
SELECT
    s.id,
    s.name,
    s.type,
    s.is_active,
    s.last_scraped_at,
    COUNT(a.id) as total_articles,
    AVG(a.score) as avg_score,
    AVG(COALESCE(a.upvotes, 0) + COALESCE(a.comments_count, 0)) as avg_engagement
FROM sources s
LEFT JOIN articles a ON s.id = a.source_id AND a.is_archived = false
GROUP BY s.id, s.name, s.type, s.is_active, s.last_scraped_at;
```

**Why Views?**
- Better performance (pre-aggregated data)
- Cleaner column names for DAX
- Can iterate on SQL without republishing Power BI
- Standard data warehouse pattern
- Easier testing and validation

### DAX Measure Organization

Create separate measure tables for organization (enterprise best practice):

**1. _Base Measures** (fundamental calculations)
```dax
Total Articles = COUNTROWS(vw_article_performance)
Total Upvotes = SUM(vw_article_performance[upvotes])
Total Comments = SUM(vw_article_performance[comments_count])
Avg Score = AVERAGE(vw_article_performance[score])
```

**2. _Time Intelligence** (period comparisons)
```dax
Total Articles MTD =
TOTALMTD([Total Articles], vw_article_performance[published_at])

Total Articles Previous Month =
CALCULATE(
    [Total Articles],
    DATEADD(vw_article_performance[published_at], -1, MONTH)
)

MoM Change % =
DIVIDE(
    [Total Articles] - [Total Articles Previous Month],
    [Total Articles Previous Month],
    0
) * 100

YTD Articles =
TOTALYTD([Total Articles], vw_article_performance[published_at])
```

**3. _KPI Measures** (business metrics)
```dax
Engagement Rate =
DIVIDE(
    [Total Comments],
    [Total Upvotes],
    0
)

System Health Score =
VAR SuccessRate = [Scrape Success Rate]
VAR Freshness = IF([Hours Since Last Scrape] < 6, 100, 50)
RETURN (SuccessRate * 0.6) + (Freshness * 0.4)

High Quality Articles =
CALCULATE(
    [Total Articles],
    vw_article_performance[score] > 70
)

Quality Rate % =
DIVIDE(
    [High Quality Articles],
    [Total Articles],
    0
) * 100
```

**4. _Advanced Analytics** (complex calculations)
```dax
Top Performing Source =
CALCULATE(
    FIRSTNONBLANK(vw_article_performance[source_name], 1),
    TOPN(1,
         ALL(vw_article_performance[source_name]),
         [Avg Score],
         DESC
    )
)

Trend Direction =
VAR Last7Days = CALCULATE([Total Articles], DATESINPERIOD(vw_article_performance[published_at], LASTDATE(vw_article_performance[published_at]), -7, DAY))
VAR Previous7Days = CALCULATE([Total Articles], DATESINPERIOD(vw_article_performance[published_at], LASTDATE(vw_article_performance[published_at]), -14, DAY), DATESINPERIOD(vw_article_performance[published_at], LASTDATE(vw_article_performance[published_at]), -7, DAY))
RETURN
IF(Last7Days > Previous7Days, "↑",
   IF(Last7Days < Previous7Days, "↓", "→"))
```

## Dashboard Pages

### Page 1: Executive Overview

**Purpose:** High-level health check - "How is the system performing overall?"

**Layout:**

**Top Zone: KPI Cards (4 across)**
- Total Articles (this month)
- Average Quality Score
- Active Sources
- Engagement Rate

**Middle Zone: Trend Visualizations**
- Line chart: Articles scraped per day (last 30 days)
  - Color by source (stacked or separate lines)
- Column chart: Average score by source (last 30 days)

**Bottom Zone: Top Performers Table**
- Top 10 articles by score
- Columns: Title, Source, Score, Upvotes, Comments, Published Date
- Conditional formatting: score >70 = green, <30 = red
- Clickable rows for drill-through

**Key DAX Measures:**
```dax
Articles This Month =
CALCULATE(
    [Total Articles],
    DATESINPERIOD(
        vw_article_performance[published_at],
        LASTDATE(vw_article_performance[published_at]),
        -1,
        MONTH
    )
)
```

**Learning Focus:** Basic aggregations, time intelligence, CALCULATE function

---

### Page 2: Source Performance Analysis

**Purpose:** Compare sources to identify which deliver best content

**Layout (2x2 grid):**

**Top Left: Source Quality Matrix**
- Clustered column chart: Avg Score by Source
- Data labels on bars
- Sort descending by score

**Top Right: Volume vs Quality Scatter Plot**
- X-axis: Total articles (volume)
- Y-axis: Average score (quality)
- Bubble size: Total engagement
- Color by source
- Identifies "sweet spot" sources

**Bottom Left: Source Reliability**
- Gauge charts per source:
  - Success rate %
  - Last scrape timestamp
  - Articles per scrape

**Bottom Right: Source Trends**
- Line chart: Articles per day by source (last 30 days)
- Multiple lines, one per source
- Identifies slowdowns or issues

**Key DAX Measures:**
```dax
Avg Score by Source =
CALCULATE(
    AVERAGE(vw_article_performance[score]),
    ALLEXCEPT(vw_article_performance, vw_article_performance[source_type])
)

Total Engagement =
SUM(vw_article_performance[upvotes]) +
SUM(vw_article_performance[comments_count])

Scrape Success Rate =
DIVIDE(
    COUNTROWS(FILTER(scraping_runs, scraping_runs[status] = "success")),
    COUNTROWS(scraping_runs),
    0
)
```

**Learning Focus:** ALLEXCEPT for context modification, scatter plots, combining measures

---

### Page 3: Content Analysis

**Purpose:** Understand what content characteristics drive success

**Layout:**

**Top Section: Category Performance**
- Stacked bar chart: Article count by category
- Secondary axis: Average engagement per category
- Date range slicer

**Middle Left: Article Length Impact**
- Scatter plot: Read time vs Score
- Trend line enabled
- Color by category
- Insight: Do longer articles score better?

**Middle Right: Tag Analysis**
- Bar chart: Most common tags (top 10)
- Length = article count with that tag
- Filter by high-scoring articles only (score >70)

**Bottom Left: Publishing Time Patterns**
- Matrix heatmap: Hour of day vs Day of week
- Color intensity = article count or avg score
- Identifies best posting times

**Bottom Right: Title Characteristics**
- Histogram: Title length distribution
- Overlay: Avg score per title length bucket
- Shows optimal title length

**Key DAX Measures:**
```dax
Top Tags =
TOPN(
    10,
    VALUES(vw_article_performance[tags]),
    COUNTROWS(vw_article_performance)
)

Avg Score High Performers =
CALCULATE(
    [Avg Score],
    vw_article_performance[score] > 70
)

Hour of Day = HOUR(vw_article_performance[published_at])

Title Length = LEN(vw_article_performance[title])
```

**Learning Focus:** TOPN, custom columns, time intelligence, histogram binning

---

### Page 4: Quality & Health Monitoring

**Purpose:** System health check - ensure scrapers work correctly and data quality is good

**Layout (4 quadrants):**

**Top Left: Score Distribution**
- Histogram: Article score buckets (0-20, 21-40, 41-60, 61-80, 81-100)
- Overlay line: Cumulative percentage
- Should show normal distribution

**Top Right: Duplicate Detection**
- Card: Duplicate count
- Table: List of duplicate URLs with count
- Filter: Last 7 days only

**Bottom Left: Scraping Health Timeline**
- Timeline: Scraping runs
- Color by status (success=green, failed=red, partial=yellow)
- Shows gaps in scraping schedule

**Bottom Right: Data Freshness**
- KPI cards:
  - Hours since last scrape (per source)
  - Articles scraped today vs 7-day avg
  - Stale articles (>30 days) percentage
- Gauge chart: Overall system health score (0-100)

**Key DAX Measures:**
```dax
Duplicate Count =
COUNTROWS(
    FILTER(
        SUMMARIZE(
            vw_article_performance,
            vw_article_performance[url],
            "Count", COUNTROWS(vw_article_performance)
        ),
        [Count] > 1
    )
)

Hours Since Last Scrape =
DATEDIFF(
    MAX(scraping_runs[completed_at]),
    NOW(),
    HOUR
)

System Health Score =
VAR SuccessRate = [Scrape Success Rate]
VAR FreshnessScore = IF([Hours Since Last Scrape] < 6, 100, 100 - ([Hours Since Last Scrape] * 2))
RETURN (SuccessRate * 0.6) + (FreshnessScore * 0.4)
```

**Learning Focus:** Data quality measures, FILTER + SUMMARIZE, time calculations, composite metrics

---

### Page 5: Trends & Insights

**Purpose:** Identify trends over time and predict what's coming next

**Layout:**

**Top Zone: Category Trending**
- Area chart: Article count by category (last 90 days)
- Stacked view shows category mix evolution
- Trend lines per category

**Middle Left: Keyword Momentum**
- Table with sparklines:
  - Keyword | Last 7 days | Last 30 days | Trend arrow | Change %
- Sort by biggest movers
- Conditional formatting: Green (growing), Red (declining)

**Middle Right: Engagement Evolution**
- Dual-axis line chart:
  - Primary: Average score over time
  - Secondary: Average engagement
- Shows if quality/engagement patterns are changing

**Bottom Zone: Predictive Insights Panel**
- Forecasting line chart: Next 30 days article volume
  - Uses Power BI's built-in forecasting
- KPI Cards with insights:
  - "Fastest growing category this month"
  - "Most active source this week"
  - "Peak engagement day/time"

**Key DAX Measures:**
```dax
Change Percentage =
DIVIDE(
    [Total Articles] - [Total Articles Previous Period],
    [Total Articles Previous Period],
    0
) * 100

Fastest Growing Category =
FIRSTNONBLANK(
    TOPN(1,
         VALUES(vw_article_performance[category]),
         [Change Percentage],
         DESC
    ),
    1
)
```

**Learning Focus:** Period-over-period analysis, forecasting, dynamic text measures, TOPN with measures

## Power BI Embedded Integration (Phase 2)

**Note:** Build in Power BI Desktop first, then integrate into web app later

### Backend: Token Generation Endpoint

**File:** `backend/app/api/powerbi.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from app.config import settings
import requests
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/powerbi/embed-token")
async def get_embed_token():
    """
    Generate Power BI embed token for frontend

    Requires:
    - Power BI Pro license
    - Azure AD app registration
    - Published report in Power BI Service
    """
    try:
        # Azure AD authentication
        auth_url = f"https://login.microsoftonline.com/{settings.POWERBI_TENANT_ID}/oauth2/v2.0/token"

        auth_data = {
            'grant_type': 'client_credentials',
            'client_id': settings.POWERBI_CLIENT_ID,
            'client_secret': settings.POWERBI_CLIENT_SECRET,
            'scope': 'https://analysis.windows.net/powerbi/api/.default'
        }

        auth_response = requests.post(auth_url, data=auth_data)
        auth_response.raise_for_status()
        access_token = auth_response.json()['access_token']

        # Generate embed token
        embed_url = f"https://api.powerbi.com/v1.0/myorg/groups/{settings.POWERBI_WORKSPACE_ID}/reports/{settings.POWERBI_REPORT_ID}/GenerateToken"

        embed_body = {
            'accessLevel': 'View',
            'allowSaveAs': False
        }

        headers = {'Authorization': f'Bearer {access_token}'}
        embed_response = requests.post(embed_url, json=embed_body, headers=headers)
        embed_response.raise_for_status()

        return {
            'token': embed_response.json()['token'],
            'embedUrl': embed_response.json()['embedUrl'],
            'reportId': settings.POWERBI_REPORT_ID,
            'expiresAt': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate embed token: {str(e)}")
```

### Frontend: Embed Component

**File:** `frontend/components/PowerBIDashboard.tsx`

```typescript
'use client';

import { useEffect, useRef, useState } from 'react';
import { models, service, factories } from 'powerbi-client';

interface EmbedToken {
  token: string;
  embedUrl: string;
  reportId: string;
}

export const PowerBIDashboard = () => {
  const reportContainer = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const embedReport = async () => {
      try {
        // Fetch embed token from backend
        const response = await fetch('/api/powerbi/embed-token');
        const embedData: EmbedToken = await response.json();

        // Power BI embed configuration
        const config: models.IReportEmbedConfiguration = {
          type: 'report',
          tokenType: models.TokenType.Embed,
          accessToken: embedData.token,
          embedUrl: embedData.embedUrl,
          id: embedData.reportId,
          permissions: models.Permissions.Read,
          settings: {
            panes: {
              filters: { expanded: false, visible: true },
              pageNavigation: { visible: true, position: models.PageNavigationPosition.Left }
            },
            background: models.BackgroundType.Transparent,
            layoutType: models.LayoutType.Custom,
            customLayout: {
              displayOption: models.DisplayOption.FitToWidth
            }
          }
        };

        // Embed the report
        const powerbi = new service.Service(
          factories.hpmFactory,
          factories.wpmpFactory,
          factories.routerFactory
        );

        const report = powerbi.embed(reportContainer.current!, config);

        // Handle events
        report.on('loaded', () => {
          console.log('Power BI report loaded');
          setLoading(false);
        });

        report.on('error', (event) => {
          console.error('Power BI error:', event.detail);
          setError('Failed to load dashboard');
          setLoading(false);
        });

      } catch (err) {
        console.error('Embed error:', err);
        setError('Failed to initialize dashboard');
        setLoading(false);
      }
    };

    embedReport();
  }, []);

  return (
    <div className="w-full h-screen">
      {loading && (
        <div className="flex items-center justify-center h-full">
          <p>Loading dashboard...</p>
        </div>
      )}
      {error && (
        <div className="flex items-center justify-center h-full text-red-500">
          <p>{error}</p>
        </div>
      )}
      <div
        ref={reportContainer}
        className="w-full h-full"
        style={{ minHeight: '600px' }}
      />
    </div>
  );
};
```

### Configuration

**Environment Variables:**

```bash
# Power BI Embedded
POWERBI_TENANT_ID=your-azure-tenant-id
POWERBI_CLIENT_ID=your-app-client-id
POWERBI_CLIENT_SECRET=your-app-secret
POWERBI_WORKSPACE_ID=your-workspace-id
POWERBI_REPORT_ID=your-report-id
```

## Implementation Plan

### Phase 1: Standalone Dashboard (Weeks 1-3)

**Week 1: Foundation**
1. Create SQL views in `database/powerbi/views.sql`
2. Run database migration to add views
3. Test views with psql queries
4. Download and install Power BI Desktop (free)
5. Connect Power BI to local PostgreSQL database
6. Create data model and relationships

**Week 2: Core Pages**
1. Build Page 1 (Executive Overview)
   - Create base DAX measures
   - Layout KPI cards, charts, table
2. Build Page 2 (Source Performance)
   - Learn scatter plots and gauge charts
   - Source comparison visuals
3. Build Page 3 (Content Analysis)
   - Advanced visuals (heatmap, histogram)
   - Tag analysis and patterns

**Week 3: Advanced Pages + Polish**
1. Build Page 4 (Quality & Health)
   - Data quality measures
   - Timeline visualizations
2. Build Page 5 (Trends & Insights)
   - Time series analysis
   - Forecasting feature
3. Apply consistent theme and colors
4. Add bookmarks for different views
5. Optimize performance
6. Save portfolio-ready .pbix file

### Phase 2: Web Integration (Week 4 - Optional)

**Prerequisites:**
- Power BI Pro license ($10/month)
- Azure account (free tier works)
- Completed Phase 1 dashboard

**Steps:**
1. Publish report to Power BI Service (powerbi.com)
2. Create Azure AD app registration
3. Configure app permissions for Power BI API
4. Implement backend token endpoint
5. Install powerbi-client npm package
6. Create frontend embed component
7. Test embedded dashboard locally
8. Deploy to production

## Testing Strategy

### Data Quality Tests

```sql
-- Test view row counts
SELECT COUNT(*) FROM vw_article_performance;
SELECT COUNT(*) FROM vw_daily_metrics;
SELECT COUNT(*) FROM vw_source_stats;

-- Validate no NULLs in critical fields
SELECT COUNT(*) FROM vw_article_performance WHERE score IS NULL;
SELECT COUNT(*) FROM vw_article_performance WHERE source_name IS NULL;

-- Check date ranges
SELECT MIN(published_at), MAX(published_at) FROM vw_article_performance;

-- Verify aggregations match
SELECT
    COUNT(*) as total_from_view,
    (SELECT COUNT(*) FROM articles WHERE is_archived = false) as total_from_table;
```

### Dashboard Validation Checklist

**Performance:**
- [ ] All pages load in <3 seconds
- [ ] Filters respond instantly
- [ ] No errors in data model
- [ ] Visuals refresh smoothly

**Data Accuracy:**
- [ ] KPIs show sensible values
- [ ] Charts display correct data
- [ ] Drill-throughs work properly
- [ ] Tooltips are informative

**Visual Quality:**
- [ ] Consistent color scheme
- [ ] Readable fonts and labels
- [ ] Mobile view works
- [ ] No overlapping elements

### Learning Checkpoints

- [ ] Understand basic DAX (SUM, AVERAGE, COUNT, DIVIDE)
- [ ] Can create time intelligence measures (MTD, YTD, Prior Period)
- [ ] Know how to use CALCULATE and FILTER
- [ ] Comfortable with 10+ visual types
- [ ] Can create custom columns and measures
- [ ] Understand data modeling and relationships
- [ ] Know how to publish reports
- [ ] Understand Power BI Embedded basics (if Phase 2 complete)

## Portfolio & Career Impact

**Deliverables:**
1. **Power BI .pbix file** - Portable, can demo in interviews
2. **Screenshots of each page** - For resume/portfolio
3. **DAX measure library** - Show technical skills
4. **Design document** - Demonstrates planning ability
5. **Embedded integration** (if Phase 2) - Full-stack capability

**Interview Talking Points:**
- "Built 5-page analytics dashboard with 20+ DAX measures"
- "Created SQL views for optimized Power BI data model"
- "Implemented Power BI Embedded with Next.js and FastAPI"
- "Analyzed content performance across multiple data sources"
- "Used time intelligence, forecasting, and advanced visualizations"

**Skills Demonstrated:**
- Power BI Desktop proficiency
- DAX language (beginner to intermediate)
- SQL view optimization
- Data modeling
- Visual design and UX
- Power BI Embedded (if Phase 2)
- Azure AD integration (if Phase 2)

## Success Metrics

**Technical:**
- All 5 pages built and functional
- 20+ DAX measures created
- Dashboard loads in <3 seconds
- Zero data quality issues
- Successfully embedded (if Phase 2)

**Learning:**
- Comfortable building new Power BI reports independently
- Can explain DAX measures in interviews
- Understand when to use different visual types
- Know embedding architecture

**Business Value:**
- Can identify best-performing content sources
- Understand what content characteristics matter
- Monitor system health effectively
- Spot trends before they peak

## Files Created

```
ZenWatch/
├── database/
│   └── powerbi/
│       └── views.sql                    # SQL view definitions
├── backend/
│   └── app/
│       └── api/
│           └── powerbi.py              # Token generation endpoint (Phase 2)
├── frontend/
│   └── components/
│       └── PowerBIDashboard.tsx        # Embed component (Phase 2)
├── powerbi/
│   └── ZenWatch_Analytics.pbix         # Power BI Desktop file
└── docs/
    └── plans/
        └── 2026-01-03-powerbi-analytics-design.md  # This document
```

## References

- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)
- [DAX Reference](https://dax.guide/)
- [Power BI Embedded](https://docs.microsoft.com/en-us/power-bi/developer/embedded/)
- [Best Practices for Power BI](https://docs.microsoft.com/en-us/power-bi/guidance/)

---

**Next Steps:**
1. Create SQL views
2. Download Power BI Desktop
3. Connect to database
4. Start building Page 1

**Estimated Time:** 3-4 weeks (Phase 1), +1 week (Phase 2)

**Last Updated:** 2026-01-03
