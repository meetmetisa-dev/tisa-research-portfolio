# Portfolio website

Static, dependency-free and ready for GitHub Pages.

## Local preview

```bash
python3 -m http.server 8000 --directory website
```

The repository includes a Pages deployment workflow. Before publishing:

1. Confirm all public degree and publication wording against source records.
2. Keep the final CV at `website/assets/Tisa_Selma_Research_CV.pdf`.
3. If the repository will not be `meetmetisa-dev/tisa-research-portfolio`, update the four project source links in `index.html`.
4. In GitHub, choose **Settings → Pages → Source: GitHub Actions**, then push to `main`.

The interactive demonstrations run entirely in the browser using synthetic inputs. No visitor data is sent anywhere by this site.
