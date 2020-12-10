#!/bin/bash -e

#set -x

clean() {
  organization=$1
  box_name=$2
  if [[ -d /tmp/vagrant/test/"${organization}"/"${box_name}" ]]; then
    cd /tmp/vagrant/test/"${organization}"/"${box_name}"
    vagrant destroy -f
  fi

  rm -rf /tmp/vagrant/build/"${organization}"/"${box_name}"

  vagrant box remove "${organization}"/"${box_name}" || true
}

build() {
  template_path=$1
  echo packer build --force "${template_path}"
  packer build --force "${template_path}"
}

test() {
  organization=$1
  box_name=$2
  test_folder=/tmp/vagrant/test/"${organization}"/"${box_name}"
  mkdir -p "${test_folder}"
  cd "${test_folder}"
  vagrant box add --name "${organization}"/"${box_name}" ~/.vagrant/boxes/"${organization}"/"${box_name}"/package.box
  vag init "${organization}"/"${box_name}"
  vagrant up
  pwd
}

push() {
  organization=$1
  box_name=$2
  scp -r /tmp/vagrant/build/"${organization}"/"${box_name}" vagrant@tmt:/home/vagrant/.vagrant/boxes/"${organization}"
}

metadata() {
  organization=$1
  box_name=$2
  scp -r /tmp/vagrant/metadata/"${organization}"/"${box_name}" \
      vagrant@tmt:/home/vagrant/.vagrant/"${organization}"
}

ssh() {
  organization=$1
  box_name=$2
  test_folder=/tmp/vagrant/test/"${organization}"/"${box_name}"
  cd "${test_folder}"
  vagrant ssh
}

usage() {
  echo -e "Example : box.sh clean 7onetella consul-cluster"
  echo
  echo -e "Example : box.sh build /tmp/vagrant/templates/consul-cluster.json"
  echo
  echo -e "Example : box.sh test 7onetella consul-cluster"
  echo
  echo -e "Example : box.sh push 7onetella consul-cluster"
  echo
  echo -e "Example : box.sh ssh 7onetella consul-cluster"
}

case $1 in
build)
  shift
  build $1
  ;;
clean)
  shift
  clean $1 $2
  ;;
test)
  shift
  test $1 $2
  ;;
ssh)
  shift
  ssh $1 $2
  ;;
push)
  shift
  push $1 $2
  ;;
metadata)
  shift
  metadata $1 $2
  ;;
--help)
  usage
  ;;
*) usage ;;
esac
