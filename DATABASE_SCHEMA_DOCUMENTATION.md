# Database Schema Documentation
## Azure SQL Database - Retail Recommendation System

**Database:** `sqldb-yompagai-dev`  
**Server:** `sql-yompagai-dev.database.windows.net`  
**Documentation Generated:** July 21, 2025  
**Data Processing Date:** July 14, 2025

---

## 📋 Table of Contents
- [Overview](#overview)
- [Database Statistics](#database-statistics)
- [Table Schemas](#table-schemas)
- [Data Relationships](#data-relationships)
- [Business Logic](#business-logic)
- [Data Quality Analysis](#data-quality-analysis)
- [Usage Examples](#usage-examples)

---

## 🎯 Overview

This database supports a **Mexican retail chain recommendation system** with primary focus on:
- 🥤 **Beverage sales** (Coca-Cola products dominate)
- 🍺 **Beer distribution** (Victoria, Heineken brands)
- 🏪 **Convenience stores** in Guadalajara metropolitan area
- 📊 **ML-driven recommendation engine** (source data → recommendations)

### Architecture Pattern
```
Raw Transaction Data → Analytics Processing → Business Recommendations
     (Active)              (In Progress)           (Awaiting)
```

---

## 📊 Database Statistics

| Metric | Value |
|--------|-------|
| **Total Tables** | 8 |
| **Active Tables** | 4 (50%) |
| **Empty Tables** | 4 (50%) |
| **Primary Geographic Market** | Guadalajara, Mexico |
| **Data Freshness** | July 14, 2025 |
| **Transaction Date Range** | June 14 - June 30, 2025 |

---

## 📋 Table Schemas

### 1. RecommendedStore 🏪
**Purpose:** Master data for all store locations and characteristics  
**Status:** ✅ Active (Contains Data)  
**Primary Key:** `StoreId`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `StoreId` | int | NOT NULL | Unique store identifier |
| `BusinessUnitId` | int | NOT NULL | Business unit classification |
| `MunicipalityId` | int | NULL | Municipality reference ID |
| `Unit` | nvarchar(50) | NULL | Business unit name |
| `Municipality` | nvarchar(50) | NULL | Municipality name |
| `PostalCode` | int | NULL | Postal code for location |
| `ClientSize` | int | NULL | Customer base size classification |
| `MonthlyGroup` | nvarchar(100) | NULL | Monthly performance grouping |
| `MonthlyPOS` | int | NULL | Monthly point-of-sale transactions |
| `ProcessDate` | date | NULL | Data processing timestamp |

**Sample Data:**
- **Geographic Focus:** Guadalajara region
- **Store Classifications:** Alto, Medio Alto, Bajo, Nulo
- **Postal Code Range:** 44490 - 44977

---

### 2. RecommendedTicket 🛒
**Purpose:** Transaction history and sales data  
**Status:** ✅ Active (Contains Data)  
**Foreign Key:** `StoreId` → RecommendedStore.StoreId

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `Category` | nvarchar(100) | NULL | Product category |
| `SKU` | nvarchar(255) | NULL | Stock Keeping Unit |
| `ProductName` | nvarchar(500) | NULL | Product display name |
| `StorePrice` | float | NULL | Selling price at store |
| `StoreId` | int | NOT NULL | Store identifier (FK) |
| `TicketId` | int | NULL | Transaction ticket ID |
| `RegistrationDate_BI_DB` | date | NULL | BI system registration date |
| `Quantity` | float | NULL | Quantity sold |
| `ProcessDate` | date | NULL | Data processing timestamp |

**Product Categories:**
- **REFRESCOS** (Soft Drinks) - Dominant category
- **CERVEZAS** (Beer) - Secondary category  
- **VEGETALES** (Vegetables) - Minor category
- **GOMA DE MASCAR** (Chewing Gum) - Minor category

**Top Products:**
- Coca-Cola variants (multiple sizes: 600ml, 1.5L, 2.0L, 2.5L)
- Victoria and Heineken beer brands
- Wrigley's Orbit gum

---

### 3. RecommendedInventorySource 📦
**Purpose:** Raw inventory data and costs  
**Status:** ✅ Active (Contains Data)  
**Foreign Key:** `StoreId` → RecommendedStore.StoreId

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `StoreId` | int | NOT NULL | Store identifier (FK) |
| `SKU` | nvarchar(255) | NULL | Stock Keeping Unit |
| `Inventory` | decimal | NULL | Current inventory quantity |
| `UnitCost` | decimal | NULL | Cost per unit |
| `ProcessDate` | date | NULL | Data processing timestamp |

**Inventory Insights:**
- **Cost Range:** $0.00 - $19.16 per unit
- **Quantity Range:** 1 - 28 units per SKU per store
- **Zero Cost Items:** Some items show $0.00 cost (possible promotions/samples)

---

### 4. RecommendedPostalCode 📍
**Purpose:** Geographic reference and municipality mapping  
**Status:** ✅ Active (Contains Data)  
**Primary Key:** `PostalCode`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `PostalCode` | int | NOT NULL | Mexican postal code |
| `Municipality` | nvarchar(50) | NOT NULL | Municipality name |

**Geographic Coverage:**
- **Primary Markets:** Coyoacán, Cuajimalpa de Morelos
- **Postal Code Ranges:** 4980, 5000-5119
- **Country:** Mexico (inferred from postal code format)

---

### 5. RecommendedAssortment 📋
**Purpose:** Product assortment recommendations by store  
**Status:** ❌ Empty (Awaiting ML Processing)  
**Foreign Key:** `StoreId` → RecommendedStore.StoreId

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `StoreId` | int | NULL | Store identifier (FK) |
| `CreatedAt` | date | NULL | Recommendation creation date |
| `UpdatedAt` | date | NULL | Last update timestamp |
| `SKU` | nvarchar(250) | NULL | Recommended product SKU |
| `ProductName` | nvarchar(500) | NULL | Product display name |
| `RecommendedRetailPrice` | float | NULL | Suggested selling price |

---

### 6. RecommendedEnvironment 🏬
**Purpose:** Store environment and category analysis  
**Status:** ❌ Empty (Awaiting ML Processing)  
**Foreign Key:** `StoreId` → RecommendedStore.StoreId

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `StoreId` | int | NULL | Store identifier (FK) |
| `CreatedAt` | date | NULL | Analysis creation date |
| `UpdatedAt` | date | NULL | Last update timestamp |
| `Category` | varchar(250) | NULL | Product category |
| `ZoneAvg` | int | NULL | Zone average metric |
| `StoreAvgSku` | int | NULL | Store average SKU count |
| `CategoryTurnover` | nvarchar(50) | NULL | Category turnover rate |

---

### 7. RecommendedInventory 📊
**Purpose:** Inventory optimization recommendations  
**Status:** ❌ Empty (Awaiting ML Processing)  
**Foreign Key:** `StoreId` → RecommendedStore.StoreId

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `StoreId` | int | NULL | Store identifier (FK) |
| `CreatedAt` | date | NULL | Recommendation creation date |
| `UpdatedAt` | date | NULL | Last update timestamp |
| `SKU` | nvarchar(250) | NULL | Product SKU |
| `ProductName` | nvarchar(500) | NULL | Product display name |
| `SkuTurnover` | nvarchar(50) | NULL | SKU turnover rate |
| `Inventory` | int | NULL | Current inventory level |
| `UnitCost` | float | NULL | Cost per unit |
| `InventoryCost` | float | NULL | Total inventory cost |
| `DemandSatisfaction` | nvarchar(5) | NULL | Demand satisfaction level |
| `InventoryDays` | int | NULL | Days of inventory coverage |
| `OptimalRestockLevel` | int | NULL | Recommended restock quantity |
| `DailyLostRevenue` | float | NULL | Revenue loss from stockouts |

---

### 8. RecommendedPrice 💰
**Purpose:** Pricing recommendations and profit analysis  
**Status:** ❌ Empty (Awaiting ML Processing)  
**Foreign Key:** `StoreId` → RecommendedStore.StoreId

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `StoreId` | int | NULL | Store identifier (FK) |
| `CreatedAt` | date | NULL | Recommendation creation date |
| `UpdatedAt` | date | NULL | Last update timestamp |
| `SKU` | nvarchar(250) | NULL | Product SKU |
| `ProductName` | nvarchar(500) | NULL | Product display name |
| `StorePrice` | float | NULL | Current store price |
| `RecommendedRetailPrice` | float | NULL | Recommended selling price |
| `UnitCost` | float | NULL | Cost per unit |
| `UniteStoreProfitMargin` | float | NULL | Store profit margin per unit |
| `UnitProfitMargin` | float | NULL | Unit profit margin |
| `PriceGap` | float | NULL | Gap between current and recommended price |

---

## 🔗 Data Relationships

### Entity Relationship Diagram
```
┌─────────────────────┐
│  RecommendedStore   │ ◄── Master Data Hub
│ ┌─────────────────┐ │     (All stores)
│ │ StoreId (PK)    │ │ ◄─┐
│ │ PostalCode      │ │   │
│ │ Municipality    │ │   │
│ └─────────────────┘ │   │
└─────────────────────┘   │
          │               │
          │ Links to      │ Foreign Key
          ▼               │ Relationships
┌─────────────────────┐   │
│RecommendedPostalCode│   │
│ ┌─────────────────┐ │   │
│ │ PostalCode (PK) │ │   │
│ │ Municipality    │ │   │
│ └─────────────────┘ │   │
└─────────────────────┘   │
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│RecommendedTicket│ │RecommendedInven-│ │ Recommendation  │
│ (Transactions)  │ │torySource       │ │ Tables          │
│ ┌─────────────┐ │ │ (Raw Inventory) │ │ (ML Output)     │
│ │StoreId (FK) │ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │
│ │SKU          │ │ │ │StoreId (FK) │ │ │ │StoreId (FK) │ │
│ │Category     │ │ │ │SKU          │ │ │ │SKU          │ │
│ │Quantity     │ │ │ │Inventory    │ │ │ │Recommenda-  │ │
│ │StorePrice   │ │ │ │UnitCost     │ │ │ │tion Data    │ │
│ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Relationship Types

1. **Store-Centric Model (1:N)**
   - One store has many transactions
   - One store has many inventory items
   - One store will have many recommendations

2. **Geographic Hierarchy**
   - PostalCode → Municipality (1:1)
   - Store → PostalCode (N:1)

3. **Product Relationships**
   - SKU appears in transactions and inventory
   - Enables sales vs. inventory analysis

---

## 💼 Business Logic

### Data Flow Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Source Data   │ => │  ML Processing  │ => │ Recommendations │
│                 │    │                 │    │                 │
│ • Transactions  │    │ • Demand        │    │ • Assortment    │
│ • Inventory     │    │   Forecasting   │    │ • Pricing       │
│ • Store Info    │    │ • Price         │    │ • Inventory     │
│ • Geography     │    │   Optimization  │    │ • Environment   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Business Rules Inferred

1. **Geographic Clustering**
   - Stores grouped by municipality and postal code
   - Performance categories: Alto, Medio Alto, Bajo, Nulo

2. **Product Categories**
   - REFRESCOS (beverages) - Primary revenue driver
   - CERVEZAS (beer) - Secondary category
   - Other categories - Long tail products

3. **Pricing Strategy**
   - Variable pricing by store location
   - Cost-plus pricing model (UnitCost + Margin)

4. **Inventory Management**
   - SKU-level tracking per store
   - Zero-cost items suggest promotional inventory

---

## 🔍 Data Quality Analysis

### Data Completeness

| Table | Status | Records | Quality Issues |
|-------|--------|---------|----------------|
| RecommendedStore | ✅ Active | 10+ | Good coverage |
| RecommendedTicket | ✅ Active | 10+ | Complete transaction data |
| RecommendedInventorySource | ✅ Active | 10+ | Some zero costs |
| RecommendedPostalCode | ✅ Active | 10+ | Geographic reference complete |
| RecommendedAssortment | ❌ Empty | 0 | Awaiting processing |
| RecommendedEnvironment | ❌ Empty | 0 | Awaiting processing |
| RecommendedInventory | ❌ Empty | 0 | Awaiting processing |
| RecommendedPrice | ❌ Empty | 0 | Awaiting processing |

### Data Quality Notes

1. **Store ID Consistency:** Different stores appear in each active table - suggests data partitioning
2. **Zero Costs:** Some inventory items show $0.00 cost (promotional items?)
3. **Date Consistency:** All process dates are 2025-07-14
4. **Geographic Concentration:** Heavy focus on Guadalajara region

---

## 🔧 Usage Examples

### Query Store Information
```sql
SELECT StoreId, Municipality, PostalCode, MonthlyGroup, MonthlyPOS
FROM RecommendedStore
WHERE Municipality = 'Guadalajara'
ORDER BY MonthlyPOS DESC;
```

### Analyze Top-Selling Products
```sql
SELECT Category, ProductName, SUM(Quantity) as TotalSold
FROM RecommendedTicket
WHERE Category = 'REFRESCOS'
GROUP BY Category, ProductName
ORDER BY TotalSold DESC;
```

### Inventory Cost Analysis
```sql
SELECT StoreId, COUNT(*) as SKUCount, 
       SUM(Inventory * UnitCost) as TotalInventoryValue
FROM RecommendedInventorySource
WHERE UnitCost > 0
GROUP BY StoreId
ORDER BY TotalInventoryValue DESC;
```

### Geographic Distribution
```sql
SELECT p.Municipality, COUNT(s.StoreId) as StoreCount
FROM RecommendedPostalCode p
LEFT JOIN RecommendedStore s ON p.PostalCode = s.PostalCode
GROUP BY p.Municipality
ORDER BY StoreCount DESC;
```

---

## 📈 Recommendations for System Enhancement

### Immediate Actions
1. **Complete ML Processing Pipeline** to populate recommendation tables
2. **Implement Data Validation** for zero-cost inventory items
3. **Add Cross-Table Validation** to ensure Store ID consistency

### Future Enhancements
1. **Add Temporal Tables** for historical recommendation tracking
2. **Implement Business Rules Engine** for automated recommendations
3. **Create Data Quality Dashboards** for monitoring

---

## 📞 Support Information

**Database Connection:**
- **MCP Server URL:** https://azsql-yompmcpserv2.thankfuldune-81948d3c.eastus2.azurecontainerapps.io/mcp/
- **Health Check:** https://azsql-yompmcpserv2.thankfuldune-81948d3c.eastus2.azurecontainerapps.io/health
- **Authentication:** Azure Managed Identity

**Documentation Updates:** This document should be updated when:
- New tables are added
- Recommendation tables are populated
- Business logic changes
- Data quality issues are resolved

---
*Generated by GitHub Copilot MCP Integration - July 21, 2025*
