import asyncio
import os
import re

from dotenv import load_dotenv
from playwright.async_api import async_playwright, expect

load_dotenv()

email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

# change this to the actual products we want to add to the cart
products = [
    {
        'quantity': 2,
        'url': "https://www.continente.pt/produto/barras-de-cereais-proteina-coco-cacau-e-caju-special-k-kelloggs-6493706.html?cgid=mercearias-cereais-barras",
    },
    {
        'quantity': 6,
        'url': "https://www.continente.pt/produto/pasta-de-dentes-protecao-total-original-colgate-6456840.html?cgid=home",
    }
]

# change this to the actual address
address = {
    'postal_code': '8333-333',
    'name': 'ID of the address',
    'street': 'street potato',
    'door': '69',
    'floor': '420',
    'side': 'right',
    'city': 'potato town',
    'reference_points': 'next to my neighbor',
}


# Web crawler
async def run(playwright):
    # init config
    chromium = playwright.chromium  # or "firefox" or "webkit".
    # headless makes the browser process window to be open(more than that)
    browser = await chromium.launch(headless=False)
    page = await browser.new_page()
    # Crawling in my site
    main_page = "https://www.continente.pt/"
    await page.goto(main_page, wait_until="networkidle")

    try:
        await page.locator("//button[@id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']").click()
    except:
        print("No cookies popup")
        pass  # may or may not need it, better to reject due to anti-bot measures
    login_button = page.locator("//button[@id='headerLoginForm']")
    await login_button.click()

    # insert login information
    email_input = page.get_by_role("textbox", name="* E-mail")
    password_input = page.get_by_role("textbox", name="* Palavra-passe")

    await email_input.fill(email)
    await password_input.fill(password)

    login_btn = page.get_by_role("button", name="Entrar")
    await login_btn.click()

    await page.locator("//span[@class='header-username-wrapper']") \
        .filter(has_text=re.compile("olá", re.IGNORECASE)).inner_text()

    # navigate to each product and add them to the cart
    for product in products:
        await page.goto(product.get('url'), wait_until="networkidle")

        add_btn = page.locator(
            "//button[@class='add-to-cart js-add-to-cart js-add-to-cart-button button button--primary']")
        await add_btn.click()

        quantity = product.get('quantity')
        while quantity > 1:
            plus_btn = page.locator("//button[@class='increase-quantity-btn']")
            await plus_btn.click()
            await page.wait_for_timeout(500)  # sadly I have to wait, there's probably a better way to do this
            quantity -= 1

    # go to the checkout and address page
    await page.goto('https://www.continente.pt/checkout/entrega-pagamento/', wait_until="networkidle")
    edit_span = page.locator(".step-header--edit > .svg-wrapper").first
    await edit_span.click()

    new_address_btn = page.locator("//button[@class='button button--linked js-action-new-address']")
    await new_address_btn.click()

    # address edit modal
    postal_code_input = page.locator("//input[@id='zipCode']")
    address_name_input = page.locator("//input[@id='name']")
    street_name_input = page.locator("//input[@id='address1']")
    door_input = page.locator("//input[@id='door']")
    floor_input = page.locator("//input[@id='floor']")
    side_input = page.locator("//input[@id='side']")
    city_input = page.locator("//input[@id='city']")
    reference_points_input = page.locator("//textarea[@id='referencePoints']")

    await postal_code_input.fill(address.get("postal_code", ""))
    await address_name_input.fill(address.get("name", ""))
    await street_name_input.fill(address.get("street", ""))
    await door_input.fill(address.get("door", ""))
    await floor_input.fill(address.get("floor", ""))
    await side_input.fill(address.get("side", ""))
    await city_input.fill(address.get("city", ""))
    await reference_points_input.fill(address.get("reference_points", ""))

    save_address_btn = page.locator("//button[@type='submit']").filter(has_text="Guardar e Selecionar")
    await save_address_btn.click()

    try:
        await expect(
            page.locator("//button[@class='button button--primary js-confirm-coverage-select']").to_be_visible(
                timeout=1000))

        confirm_btn = page.locator("//button[@class='button button--primary js-confirm-coverage-select']").filter(
            has_text="Confirmar")
        await confirm_btn.click()
    except:
        print("There is no confirm.")
        pass
    await page.wait_for_load_state("networkidle")

    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


asyncio.run(main())
