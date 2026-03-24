---
name: oci-yolo-ds-analysis
description: This skill provides the ability to analysis the YOLO dataset format in OCI bucket to detect anomaly and inconsistencies in the dataset, such as missing labels, incorrect bounding boxes, and class imbalances. It can also generate reports and visualizations to help users understand the quality of their dataset and make informed decisions about data preprocessing and model training.
disable-model-invocation: true
---

# OCI YOLO Dataset Analysis Skill

## Overview

This skill analyzes YOLO-format datasets stored in OCI Object Storage buckets, detecting anomalies and inconsistencies to ensure dataset quality before model training.

---

## Inputs

The user must provide (or these must be configured via environment/context):

| Parameter | Description | Example |
|---|---|---|
| `bucket name` | OCI Object Storage bucket name | $ARGUMENTS[0] |
| `path to .oci folder` | Path to the .oci folder containing credentials | $ARGUMENTS[1] |
| `prefix` | folder prefix of dataset inside the bucket | $ARGUMENTS[2] |
| `bucket_namespace` | OCI namespace of the bucket | $ARGUMENTS[3] |

---

## YOLO Dataset Format Reference

A valid YOLO dataset in the bucket should follow this structure:

```
<prefix>/
  train/
    images/
      image_001.jpg
      image_002.jpg
    labels/
      image_001.txt
      image_002.txt
  val/
    images/
      image_003.jpg
      image_004.jpg
    labels/
      image_003.txt
      image_004.txt
  test/
    images/
      image_005.jpg
      image_006.jpg
    labels/
      image_005.txt
      image_006.txt
  data.yaml          # or classes.txt
```

Each `.txt` label file follows the format:
```
<class_id> <x_center> <y_center> <width> <height>
```
- All values normalized between `0.0` and `1.0`
- One annotation per line
- Empty file = valid image with no objects (background)

---

## Analysis Checks

### 1. Label-Image Pairing
- [ ] Every image has a corresponding label file
- [ ] Every label file has a corresponding image
- [ ] Orphan images (no label) → list and count
- [ ] Orphan labels (no image) → list and count

### 2. Bounding Box Validation
- [ ] All coordinates within `[0.0, 1.0]`
- [ ] Width and height > 0
- [ ] No degenerate boxes (area ≈ 0)
- [ ] Detect boxes with extreme aspect ratios (configurable threshold)

### 3. Class Distribution
- [ ] Count annotations per class across train/val/test splits
- [ ] Detect classes with zero annotations
- [ ] Detect severe class imbalance (configurable ratio threshold)
- [ ] Validate all class IDs against `classes.txt` / `data.yaml`
- [ ] Flag unknown class IDs (out of range)

### 4. Dataset Split Integrity
- [ ] Verify train/val/test splits exist
- [ ] Check for image leakage between splits (same filename in multiple splits)
- [ ] Report split ratios

### 5. File Format Checks
- [ ] Images are readable (not corrupted)
- [ ] Label files have valid numeric content
- [ ] Encoding issues in label files

### 6. Duplicate Detection
- [ ] Exact filename duplicates within a split
- [ ] (Optional) Hash-based image duplicate detection

---

## Output / Report

The analysis produces a structured report with:

```
summary:
  total_images: int
  total_labels: int
  orphan_images: int
  orphan_labels: int
  invalid_boxes: int
  unknown_classes: int
  duplicate_files: int

class_distribution:
  <class_name>: { train: int, val: int, test: int }

anomalies:
  - type: <check_type>
    severity: low | medium | high
    file: <file_path_in_bucket>
    detail: <human-readable description>

split_ratios:
  train: float
  val: float
  test: float
```

Report is saved as:
- `report.json` — machine-readable full report
- `report.html` — (optional) human-readable with charts

---

## Bucket OCI References

- get The bucket oci references in file on `templates/manipule_bucket_data.py` for examples of how to reference the bucket and prefix in code and environment variables.

---


# Output

The output of this skill is a comprehensive report detailing the quality and integrity of the YOLO dataset in the specified OCI bucket, including any detected anomalies and recommendations for improvement. This report can be formatted as PDF and is saved in the specified output ($ARGUMENTS[4]) location for user review and action. 
