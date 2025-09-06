"""
K-Anonymity Implementation - Main Execution Script

Complete pipeline for k-anonymity algorithm with metrics calculation.
Demonstrates the full process from data loading to results export.

Usage: python main.py
"""

from k_anonymity import KAnonymityEngine
from metrics import PrivacyMetrics
import pandas as pd


def run_full_pipeline(sample_size=500, k_distribution=None):
    """
    Run complete k-anonymity pipeline with metrics
    
    Args:
        sample_size: Number of records to process (None for full dataset)
        k_distribution: Dict of k-values and counts for testing
    """
    print("K-ANONYMITY IMPLEMENTATION PIPELINE")
    print("=" * 60)
    
    # Step 1: Initialize components
    print("\n1. Initializing K-Anonymity Engine...")
    engine = KAnonymityEngine()
    metrics_calc = PrivacyMetrics()
    
    # Step 2: Load and prepare dataset
    print("\n2. Loading Adult Dataset...")
    df = engine.load_data('../datasets/adult.data', sample_size=sample_size)
    original_df = df.copy()  # Keep original for metrics
    
    # Set k-values for testing
    if k_distribution is None:
        k_distribution = {2: 300, 3: 100, 4: 60, 5: 40}
    
    engine.set_k_values(df, k_distribution)
    
    print(f"Dataset loaded: {len(df)} records")
    print(f"K-value distribution: {k_distribution}")
    
    # Step 3: Apply k-anonymity algorithm
    print("\n3. Applying K-Anonymity Algorithm...")
    anonymized_df = engine.anonymize(df, verbose=True)
    
    # Step 4: Calculate comprehensive metrics
    print("\n4. Calculating Privacy Metrics...")
    report = metrics_calc.generate_comprehensive_report(
        original_df, anonymized_df, engine.stats
    )
    
    # Step 5: Display results
    print("\n5. Results Summary:")
    print("-" * 30)
    print(f"Distortion: {report['privacy_metrics']['distortion']:.4f}")
    print(f"Precision: {report['privacy_metrics']['precision']:.4f}")
    print(f"Suppression Rate: {report['privacy_metrics']['suppression_rate']:.4f}")
    print(f"Utility Loss: {report['utility_metrics']['utility_loss']:.4f}")
    print(f"K-Anonymous: {report['k_anonymity_verification']['is_k_anonymous']}")
    
    # Step 6: Export results
    print("\n6. Exporting Results...")
    engine.export_results(anonymized_df)
    metrics_calc.export_report(report)
    
    print("\nPipeline completed successfully!")
    return anonymized_df, report


def run_comparison_study():
    """
    Run k-anonymity with different k-value distributions for comparison
    """
    print("K-ANONYMITY COMPARISON STUDY")
    print("=" * 60)
    
    # Different k-value scenarios
    scenarios = {
        'Low Privacy (k=2-3)': {2: 80, 3: 20},
        'Medium Privacy (k=2-4)': {2: 50, 3: 30, 4: 20},
        'High Privacy (k=3-5)': {3: 40, 4: 35, 5: 25}
    }
    
    results = {}
    
    for scenario_name, k_dist in scenarios.items():
        print(f"\n--- {scenario_name} ---")
        
        engine = KAnonymityEngine()
        metrics_calc = PrivacyMetrics()
        
        # Load fresh dataset
        df = engine.load_data('../datasets/adult.data', sample_size=200)
        original_df = df.copy()
        
        # Set scenario k-values
        engine.set_k_values(df, k_dist)
        
        # Run algorithm
        anonymized_df = engine.anonymize(df, verbose=False)
        
        # Calculate metrics
        report = metrics_calc.generate_comprehensive_report(original_df, anonymized_df)
        
        # Store results
        results[scenario_name] = {
            'distortion': report['privacy_metrics']['distortion'],
            'precision': report['privacy_metrics']['precision'],
            'suppression_rate': report['privacy_metrics']['suppression_rate'],
            'utility_loss': report['utility_metrics']['utility_loss']
        }
        
        print(f"Distortion: {report['privacy_metrics']['distortion']:.4f}")
        print(f"Suppression: {report['privacy_metrics']['suppression_rate']:.4f}")
    
    # Summary comparison
    print("\nCOMPARISON SUMMARY")
    print("-" * 40)
    print("Scenario                   | Distortion | Suppression | Utility Loss")
    print("-" * 65)
    
    for scenario, metrics in results.items():
        print(f"{scenario:25} | {metrics['distortion']:8.4f} | {metrics['suppression_rate']:9.4f} | {metrics['utility_loss']:10.4f}")


def main():
    """Main execution function"""
    print("Select execution mode:")
    print("1. Run full pipeline (default)")
    print("2. Run comparison study")
    
    try:
        choice = input("\nEnter choice (1 or 2, default=1): ").strip()
        if choice == '2':
            run_comparison_study()
        else:
            run_full_pipeline()
    except KeyboardInterrupt:
        print("\nExecution cancelled by user.")
    except Exception as e:
        print(f"\nError during execution: {e}")


if __name__ == "__main__":
    main()
