"""Read inventory data and validate it independently of file output."""
from playwright.sync_api import Page


def validate_inventory(title: str, heading: str) -> dict[str, str]:
    title, heading = title.strip(), heading.strip()
    if title != "Swag Labs" or heading != "Products":
        raise ValueError("Expected Swag Labs title and Products inventory heading")
    return {"page_title": title, "inventory_heading": heading}


def extract_inventory(page: Page, heading_selector: str) -> dict[str, str]:
    return validate_inventory(page.title(), page.locator(heading_selector).inner_text())
