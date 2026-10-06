"""Read deterministic page data and validate it independently of file output."""
from playwright.sync_api import Page


def validate_inventory(title: str, heading: str) -> dict[str, str]:
    title, heading = title.strip(), heading.strip()
    if title != "Swag Labs" or heading != "Products":
        raise ValueError("Expected Swag Labs title and Products inventory heading")
    return {"page_title": title, "inventory_heading": heading}


def extract_inventory(page: Page, heading_selector: str) -> dict[str, str]:
    return validate_inventory(page.title(), read_visible_text(page, heading_selector))


def read_visible_text(page: Page, selector: str) -> str:
    locator = page.locator(selector)
    locator.wait_for(state="visible")
    return locator.inner_text().strip()


def validate_form_result(title: str, heading: str, message: str) -> dict[str, str]:
    if (title.strip(), heading.strip(), message.strip()) != (
            "Web form - target page", "Form submitted", "Received!"):
        raise ValueError("Expected Selenium form submission confirmation")
    return {"page_title": title.strip(), "heading": heading.strip(),
            "confirmation": message.strip()}


def extract_form_result(page: Page, heading_selector: str,
                        message_selector: str) -> dict[str, str]:
    return validate_form_result(page.title(), read_visible_text(page, heading_selector),
                                read_visible_text(page, message_selector))
