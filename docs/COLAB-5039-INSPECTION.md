# Browser-based inspection without GitHub Actions

Use `notebooks/conquer_5039_read_only_inventory.ipynb` in **Google Colab** (File > Upload notebook). Click Run all. The notebook downloads the publicly archived 5039 installer to a temporary Linux VM, verifies the known 456150213-byte file size and MZ header, computes SHA-256, invokes `7z l -slt` (listing only), and downloads `conquer_5039_map_inventory.json` containing paths matching map/scene/DMap. It **does not execute the installer** or extract assets. Transfer only that small JSON file back to the conversation.

The 5039 executable itself must never be uploaded to the repo. A valid archive listing does not imply malware safety, copyright permission, or working game compatibility. If the Internet Archive refuses a Colab request, don't bypass access protections; instead supply an authorized copy via Drive after checking its access rights. Do not upload sensitive unrelated Drive files.

Colab is an optional user-authorized browser environment, not a background job or a service ChatGPT can run here. It avoids blocked GitHub-hosted runner queues and local installer execution. Avoid granting Colab Google Drive mount permissions because this notebook doesn't require them.
