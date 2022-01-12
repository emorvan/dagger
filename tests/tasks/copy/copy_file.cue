package main

import (
	"dagger.io/dagger/engine"
)

engine.#Plan & {
	actions: {
		alpine3_15_0: engine.#Pull & {
			source: "alpine:3.15.0@sha256:e7d88de73db3d3fd9b2d63aa7f447a10fd0220b7cbf39803c803f2af9ba256b3"
		}

		busybox1_34_1: engine.#Pull & {
			source: "busybox:1.34.1-glibc@sha256:ec98391b8f0911db08be2ee6c46813eeac17b9625b402ea1ce45dcfcd05d78d6"
		}

		verify_alpine_3_15_0: engine.#ReadFile & {
			input: alpine3_15_0.output
			path:  "/etc/alpine-release"
		} & {
			// assert result
			contents: "3.15.0\n"
		}

		copy: engine.#Copy & {
			input: busybox1_34_1.output
			source: {
				root: alpine3_15_0.output
				path: "/etc/alpine-release"
			}
			dest: "/alpine3_15_0_release"
		}

		verify_copy: engine.#ReadFile & {
			input: copy.output
			path:  "/alpine3_15_0_release"
		} & {
			// assert result
			contents: "3.15.0\n"
		}
	}
}
