package io.github.minokim.lumiawiki.fixture;

import io.github.minokim.lumiawiki.common.api.ApiExceptionAdvice;
import io.github.minokim.lumiawiki.common.api.RequestIdFilter;
import io.github.minokim.lumiawiki.dev.FoundationController;
import io.github.minokim.lumiawiki.dev.FoundationService;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

// Foundation/probe tests have their own migration and an empty entity package.
// They must not validate or install the product catalog as a side effect.
@Configuration(proxyBeanMethods = false)
@EnableAutoConfiguration
@Import({
  FoundationController.class,
  FoundationService.class,
  ApiExceptionAdvice.class,
  RequestIdFilter.class
})
public class FoundationTestApplication {}
