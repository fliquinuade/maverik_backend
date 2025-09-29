#!/usr/bin/env bash
set -e

main() {
  local project_path="$(pwd)"
  local output_path="${project_path}/dist"

#   source "${project_path}/.venv/bin/activate"
#   rm -rf "${output_path}"
  
#   curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#   .venv/bin/python get-pip.py
  
#   uv pip compile pyproject.toml > requirements.txt
#   .venv/bin/pip install \
#     --no-color \
#     --quiet \
#     --requirement "${project_path}/requirements.txt" \
#     --target "${output_path}/layer/python"

#   mkdir "${output_path}/layer/lib"
  cp "${project_path}/libsodium.so.26.1.0" "${output_path}/layer/lib/libsodium.so"

  zip -qr "${output_path}/lambda.zip" "maverik_backend"

  cd "${output_path}/layer"
  zip -qr "${output_path}/layer.zip" .

#   mkdir "${output_path}/to_publish"
  mv "${output_path}/lambda.zip" "${output_path}/to_publish/"
  mv "${output_path}/layer.zip" "${output_path}/to_publish/"

  aws s3 cp --recursive "${output_path}/to_publish" "s3://maverik-backend-s3"

  cd - &>/dev/null
}

# call main
main "${@}"
