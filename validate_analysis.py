#!/usr/bin/env python3
"""
Analysis Validation Script

This script validates the analytical claims made in the Genie-generated report
against the raw P&L data to ensure accuracy and consistency.

Usage:
    python validate_analysis.py
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import json


@dataclass
class ValidationResult:
    """Result of validating an analytical claim"""
    claim: str
    expected_value: Any
    actual_value: Any
    variance: float
    is_valid: bool
    notes: str = ""


class PandaAnalysisValidator:
    """Validate analytical claims against raw P&L data"""
    
    def __init__(self, csv_file: str):
        """Load and prepare the P&L data"""
        self.df = pd.read_csv(csv_file)
        self.store_number = "1619"
        self.period = "202507"
        self.validation_results: List[ValidationResult] = []
        
        print(f"📊 Loaded P&L data: {len(self.df)} rows")
        print(f"🏪 Store: {self.store_number}, Period: {self.period}")
        
    def validate_revenue_claims(self) -> List[ValidationResult]:
        """Validate revenue-related claims from the analysis"""
        results = []
        
        # Claim 1: Food Sales $320,433 vs plan $341,386 (-6.1%)
        food_sales = self.df[
            (self.df['Type'] == 'Net Sales') & 
            (self.df['LineItem'].str.contains('Sales_Food', na=False))
        ]
        
        if not food_sales.empty:
            actual = food_sales['Actual'].iloc[0]
            plan = food_sales['Plan'].iloc[0]
            variance_pct = ((actual - plan) / plan * 100) if plan != 0 else 0
            
            results.append(ValidationResult(
                claim="Food Sales: $320,433 actual vs $341,386 plan (-6.1%)",
                expected_value={"actual": 320433, "plan": 341386, "variance": -6.1},
                actual_value={"actual": actual, "plan": plan, "variance": variance_pct},
                variance=abs(variance_pct - (-6.1)),
                is_valid=abs(actual - 320433) < 1 and abs(plan - 341386) < 1,
                notes=f"Raw data shows: Actual=${actual:,.0f}, Plan=${plan:,.0f}, Variance={variance_pct:.1f}%"
            ))
        
        # Claim 2: Beverage Sales $15,826 vs $19,442 plan (-18.6%)
        beverage_sales = self.df[
            (self.df['Type'] == 'Net Sales') & 
            (self.df['LineItem'].str.contains('Sales_Beverage', na=False))
        ]
        
        if not beverage_sales.empty:
            actual = beverage_sales['Actual'].iloc[0]
            plan = beverage_sales['Plan'].iloc[0]
            variance_pct = ((actual - plan) / plan * 100) if plan != 0 else 0
            
            results.append(ValidationResult(
                claim="Beverage Sales: $15,826 actual vs $19,442 plan (-18.6%)",
                expected_value={"actual": 15826, "plan": 19442, "variance": -18.6},
                actual_value={"actual": actual, "plan": plan, "variance": variance_pct},
                variance=abs(variance_pct - (-18.6)),
                is_valid=abs(actual - 15826) < 1 and abs(plan - 19442) < 1,
                notes=f"Raw data shows: Actual=${actual:,.0f}, Plan=${plan:,.0f}, Variance={variance_pct:.1f}%"
            ))
        
        # Claim 3: Retail Revenue -30.8% variance
        retail_sales = self.df[
            (self.df['Type'] == 'Net Sales') & 
            (self.df['LineItem'].str.contains('Sales_Retail', na=False))
        ]
        
        if not retail_sales.empty:
            actual = retail_sales['Actual'].iloc[0]
            plan = retail_sales['Plan'].iloc[0]
            variance_pct = ((actual - plan) / plan * 100) if plan != 0 else 0
            
            results.append(ValidationResult(
                claim="Retail Sales variance: -30.8%",
                expected_value=-30.8,
                actual_value=variance_pct,
                variance=abs(variance_pct - (-30.8)),
                is_valid=abs(variance_pct - (-30.8)) < 1,
                notes=f"Raw data shows: Actual=${actual:.0f}, Plan=${plan:.0f}, Variance={variance_pct:.1f}%"
            ))
        
        return results
    
    def validate_profitability_claims(self) -> List[ValidationResult]:
        """Validate profitability-related claims"""
        results = []
        
        # Claim 1: Restaurant Contribution $562,065 vs $598,443 (-6.1%)
        restaurant_contrib = self.df[self.df['Type'] == 'Restaurant Contribution']
        
        if not restaurant_contrib.empty:
            actual = restaurant_contrib['Actual'].iloc[0]
            plan = restaurant_contrib['Plan'].iloc[0]
            variance_pct = ((actual - plan) / plan * 100) if plan != 0 else 0
            
            results.append(ValidationResult(
                claim="Restaurant Contribution: $562,065 vs $598,443 (-6.1%)",
                expected_value={"actual": 562065, "plan": 598443, "variance": -6.1},
                actual_value={"actual": actual, "plan": plan, "variance": variance_pct},
                variance=abs(variance_pct - (-6.1)),
                is_valid=abs(actual - 562065) < 1 and abs(plan - 598443) < 1,
                notes=f"Raw data shows: Actual=${actual:,.0f}, Plan=${plan:,.0f}, Variance={variance_pct:.1f}%"
            ))
        
        # Claim 2: Controllable Profit -6.6% variance
        controllable_profit = self.df[self.df['Type'] == 'Controllable Profit']
        
        if not controllable_profit.empty:
            actual = controllable_profit['Actual'].iloc[0]
            plan = controllable_profit['Plan'].iloc[0]
            variance_pct = ((actual - plan) / plan * 100) if plan != 0 else 0
            
            results.append(ValidationResult(
                claim="Controllable Profit variance: -6.6%",
                expected_value=-6.6,
                actual_value=variance_pct,
                variance=abs(variance_pct - (-6.6)),
                is_valid=abs(variance_pct - (-6.6)) < 0.1,
                notes=f"Raw data shows: Actual=${actual:,.0f}, Plan=${plan:,.0f}, Variance={variance_pct:.1f}%"
            ))
        
        return results
    
    def validate_promotional_claims(self) -> List[ValidationResult]:
        """Validate promotional spending claims"""
        results = []
        
        # Claim: Sales Promotions $19,458 vs $14,164 (+37.4%)
        promotions = self.df[
            (self.df['Type'] == 'Net Sales') & 
            (self.df['LineItem'].str.contains('Sales_Promotion', na=False))
        ]
        
        if not promotions.empty:
            actual = abs(promotions['Actual'].iloc[0])  # Take absolute value since it's negative
            plan = abs(promotions['Plan'].iloc[0])
            variance_pct = ((actual - plan) / plan * 100) if plan != 0 else 0
            
            results.append(ValidationResult(
                claim="Sales Promotions: $19,458 vs $14,164 (+37.4%)",
                expected_value={"actual": 19458, "plan": 14164, "variance": 37.4},
                actual_value={"actual": actual, "plan": plan, "variance": variance_pct},
                variance=abs(variance_pct - 37.4),
                is_valid=abs(actual - 19458) < 1 and abs(plan - 14164) < 1,
                notes=f"Raw data shows: Actual=${actual:,.0f}, Plan=${plan:,.0f}, Variance={variance_pct:.1f}%"
            ))
        
        return results
    
    def validate_employee_meals_claims(self) -> List[ValidationResult]:
        """Validate employee meals variance claims"""
        results = []
        
        # Claim: Employee Meals $5,882 vs $10,454 (-43.7%)
        employee_meals = self.df[
            (self.df['Type'] == 'Net Sales') & 
            (self.df['LineItem'].str.contains('Employee_Meals', na=False))
        ]
        
        if not employee_meals.empty:
            actual = abs(employee_meals['Actual'].iloc[0])
            plan = abs(employee_meals['Plan'].iloc[0])
            variance_pct = ((actual - plan) / plan * 100) if plan != 0 else 0
            
            results.append(ValidationResult(
                claim="Employee Meals: $5,882 vs $10,454 (-43.7%)",
                expected_value={"actual": 5882, "plan": 10454, "variance": -43.7},
                actual_value={"actual": actual, "plan": plan, "variance": variance_pct},
                variance=abs(variance_pct - (-43.7)),
                is_valid=abs(actual - 5882) < 1 and abs(plan - 10454) < 1,
                notes=f"Raw data shows: Actual=${actual:,.0f}, Plan=${plan:,.0f}, Variance={variance_pct:.1f}%"
            ))
        
        return results
    
    def validate_summary_metrics(self) -> List[ValidationResult]:
        """Validate key summary metrics from the financial impact table"""
        results = []
        
        # Financial Impact Summary validation
        financial_claims = [
            {
                "metric": "Food Sales",
                "type_filter": "Net Sales",
                "line_item_filter": "Sales_Food",
                "expected": {"actual": 320433, "plan": 341386, "variance": -6.1}
            },
            {
                "metric": "Beverage Sales", 
                "type_filter": "Net Sales",
                "line_item_filter": "Sales_Beverage",
                "expected": {"actual": 15826, "plan": 19442, "variance": -18.6}
            },
            {
                "metric": "Controllable Profit",
                "type_filter": "Controllable Profit",
                "line_item_filter": None,
                "expected": {"actual": 539814, "plan": 577730, "variance": -6.6}
            }
        ]
        
        for claim in financial_claims:
            if claim["line_item_filter"]:
                data = self.df[
                    (self.df['Type'] == claim["type_filter"]) & 
                    (self.df['LineItem'].str.contains(claim["line_item_filter"], na=False))
                ]
            else:
                data = self.df[self.df['Type'] == claim["type_filter"]]
            
            if not data.empty:
                actual = data['Actual'].iloc[0]
                plan = data['Plan'].iloc[0]
                variance_pct = ((actual - plan) / plan * 100) if plan != 0 else 0
                
                # Handle negative values (like promotions)
                if actual < 0:
                    actual = abs(actual)
                    plan = abs(plan)
                
                expected = claim["expected"]
                is_valid = (
                    abs(actual - expected["actual"]) < 1 and
                    abs(plan - expected["plan"]) < 1 and
                    abs(variance_pct - expected["variance"]) < 0.5
                )
                
                results.append(ValidationResult(
                    claim=f"{claim['metric']} summary metrics",
                    expected_value=expected,
                    actual_value={"actual": actual, "plan": plan, "variance": variance_pct},
                    variance=abs(variance_pct - expected["variance"]),
                    is_valid=is_valid,
                    notes=f"Validation for {claim['metric']} financial impact table"
                ))
        
        return results
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation checks and return comprehensive results"""
        print("\n🔍 Starting comprehensive analysis validation...\n")
        
        # Run all validation categories
        revenue_results = self.validate_revenue_claims()
        profitability_results = self.validate_profitability_claims()
        promotional_results = self.validate_promotional_claims()
        employee_meals_results = self.validate_employee_meals_claims()
        summary_results = self.validate_summary_metrics()
        
        # Combine all results
        all_results = (
            revenue_results + profitability_results + promotional_results + 
            employee_meals_results + summary_results
        )
        
        self.validation_results = all_results
        
        # Calculate summary statistics
        total_validations = len(all_results)
        valid_count = sum(1 for r in all_results if r.is_valid)
        invalid_count = total_validations - valid_count
        accuracy_rate = (valid_count / total_validations * 100) if total_validations > 0 else 0
        
        # Print detailed results
        print("=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        
        for i, result in enumerate(all_results, 1):
            status = "✅ VALID" if result.is_valid else "❌ INVALID"
            print(f"\n{i}. {status}")
            print(f"   Claim: {result.claim}")
            print(f"   Expected: {result.expected_value}")
            print(f"   Actual: {result.actual_value}")
            print(f"   Variance: {result.variance:.2f}")
            if result.notes:
                print(f"   Notes: {result.notes}")
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total validations: {total_validations}")
        print(f"Valid claims: {valid_count}")
        print(f"Invalid claims: {invalid_count}")
        print(f"Accuracy rate: {accuracy_rate:.1f}%")
        
        if accuracy_rate >= 95:
            print("🎯 EXCELLENT: Analysis is highly accurate!")
        elif accuracy_rate >= 85:
            print("✅ GOOD: Analysis is mostly accurate with minor discrepancies")
        elif accuracy_rate >= 70:
            print("⚠️  FAIR: Analysis has some accuracy issues")
        else:
            print("❌ POOR: Analysis has significant accuracy problems")
        
        return {
            "total_validations": total_validations,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "accuracy_rate": accuracy_rate,
            "detailed_results": [
                {
                    "claim": r.claim,
                    "expected": r.expected_value,
                    "actual": r.actual_value,
                    "variance": r.variance,
                    "is_valid": r.is_valid,
                    "notes": r.notes
                }
                for r in all_results
            ]
        }
    
    def validate_data_completeness(self):
        """Check data completeness and structure"""
        print("\n📋 DATA COMPLETENESS CHECK")
        print("-" * 40)
        
        # Check key data types are present
        required_types = ['Net Sales', 'Cogs', 'Labor', 'Controllables', 'Fixed Costs', 
                         'Restaurant Contribution', 'Controllable Profit']
        
        present_types = self.df['Type'].unique()
        missing_types = [t for t in required_types if t not in present_types]
        
        print(f"Required types: {len(required_types)}")
        print(f"Present types: {len(present_types)}")
        print(f"Missing types: {missing_types if missing_types else 'None'}")
        
        # Check for null values in key columns
        key_columns = ['Actual', 'Plan', 'Type', 'LineItem']
        null_counts = {col: self.df[col].isnull().sum() for col in key_columns}
        
        print(f"\nNull values by column:")
        for col, count in null_counts.items():
            print(f"  {col}: {count}")
        
        # Check data ranges
        print(f"\nData ranges:")
        print(f"  Actual values: ${self.df['Actual'].min():,.0f} to ${self.df['Actual'].max():,.0f}")
        print(f"  Plan values: ${self.df['Plan'].min():,.0f} to ${self.df['Plan'].max():,.0f}")


def main():
    """Main execution function"""
    print("🔍 Panda P&L Analysis Validation")
    print("=" * 50)
    
    try:
        # Initialize validator
        validator = PandaAnalysisValidator("store_1619_pnl.csv")
        
        # Check data completeness
        validator.validate_data_completeness()
        
        # Run comprehensive validation
        results = validator.run_all_validations()
        
        # Save results (convert numpy types and booleans for JSON serialization)
        def convert_for_json(obj):
            if hasattr(obj, 'item'):  # numpy types
                return obj.item()
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(v) for v in obj]
            return obj
        
        json_results = convert_for_json(results)
        with open("validation_results.json", "w") as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to validation_results.json")
        
    except FileNotFoundError:
        print("❌ Error: store_1619_pnl.csv not found")
        print("   Please ensure the CSV file is in the current directory")
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
