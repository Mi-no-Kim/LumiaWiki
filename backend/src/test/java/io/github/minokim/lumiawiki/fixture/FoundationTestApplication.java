package io.github.minokim.lumiawiki.fixture;

import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.context.annotation.Configuration;

// Foundation/probe tests have their own migration and an empty entity package.
// They must not validate or install the product catalog as a side effect.
@Configuration(proxyBeanMethods = false)
@EnableAutoConfiguration
public class FoundationTestApplication {}
